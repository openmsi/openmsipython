#imports
from .data_file_chunk import DataFileChunk
from .utilities import produce_from_queue_of_file_chunks
from ..my_kafka.my_producers import TutorialClusterProducer
from ..utilities.misc import populated_kwargs
from ..utilities.logging import Logger
from ..utilities.config import DATA_FILE_HANDLING_CONST, RUN_OPT_CONST, TUTORIAL_CLUSTER_CONST
from confluent_kafka import Producer
from threading import Thread, Lock
from queue import Queue
from contextlib import nullcontext
from hashlib import sha512
import os

# DataFile Class
class DataFile() :
    """
    Class for representing a single data file
    Can be used to chunk and upload a file on disk to a topic in a cluster, or reconstruct a file from stream to one on disk
    """
    def __init__(self,filepath,**kwargs) :
        """
        filepath = path to the file
        
        Possible keyword arguments:
        logger = the logger object for this file's messages to use (a new one will be created if none is supplied)
        """
        self._filepath = filepath
        self._filename = os.path.basename(filepath)
        self._logger = kwargs.get('logger')
        if self._logger is None :
            self._logger = Logger(os.path.basename(__file__).split('.')[0])
        self._chunk_offsets_added_this_run = set()

    #################### PUBLIC FUNCTIONS ####################

    def get_list_of_file_chunks(self,chunk_size) :
        """
        Build and return a list of all DataFileChunk objects for this file
        chunk_size = how many bytes of data should be in each DataFileChunk
        """
        #start a hash for the file and the lists of chunks
        file_hash = sha512()
        chunks = []
        data_file_chunks = []
        #read the binary data in the file as chunks of the given size, adding each chunk to the list 
        with open(self._filepath, "rb") as fp :
            chunk_offset = 0
            chunk = fp.read(chunk_size)
            while len(chunk) > 0:
                chunk_length = len(chunk)
                file_hash.update(chunk)
                chunk_hash = sha512()
                chunk_hash.update(chunk)
                chunk_hash = chunk_hash.digest()
                chunks.append([chunk_hash,chunk_offset,chunk_length])
                chunk_offset += chunk_length
                chunk = fp.read(chunk_size)
        file_hash = file_hash.digest()
        self._logger.info(f'File {self._filepath} has a total of {len(chunks)} chunks')
        #add all the chunks to the other list as DataFileChunk objects
        for ic,c in enumerate(chunks,start=1) :
            data_file_chunks.append(DataFileChunk(self._filepath,file_hash,c[0],c[1],c[2],self._filename,ic,len(chunks)))
        #return the list of DataFileChunks
        return data_file_chunks

    
    def upload_whole_file(self,**kwargs) :
        """
        Chunk and upload an entire file on disk to a cluster's topic.
        
        Possible keyword arguments:
        n_threads  = the number of threads to run at once during uploading
        chunk_size = the size of each file chunk in bytes
        producer   = the producer object to use
        topic_name = the name of the topic to use
        """
        #set the important variables
        kwargs = populated_kwargs(kwargs,
                                  {'n_threads': RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                   'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                   'producer': (TutorialClusterProducer(),Producer),
                                   'topic_name': TUTORIAL_CLUSTER_CONST.LECROY_FILE_TOPIC_NAME
                                  },self._logger)
        startup_msg = f"Uploading entire file {self._filepath} to {kwargs['topic_name']} in {kwargs['chunk_size']} byte chunks "
        startup_msg+=f"using {kwargs['n_threads']} threads...."
        self._logger.info(startup_msg)
        #build the upload queue
        dfcs = self.get_list_of_file_chunks(kwargs['chunk_size'])
        #add all the chunks to the upload queue
        upload_queue = Queue()
        for ic,c in enumerate(dfcs) :
            upload_queue.put(c)
        #add "None" to the queue for each thread as the final values
        for ti in range(kwargs['n_threads']) :
            upload_queue.put(None)
        #produce all the messages in the queue using multiple threads
        upload_threads = []
        lock = Lock()
        for ti in range(kwargs['n_threads']) :
            t = Thread(target=produce_from_queue_of_file_chunks, args=(upload_queue,
                                                                       kwargs['producer'],
                                                                       kwargs['topic_name'],
                                                                       self._logger,
                                                                       lock))
            t.start()
            upload_threads.append(t)
        #join the threads
        for ut in upload_threads :
            ut.join()
        self._logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
        kwargs['producer'].flush() #don't leave the function until all messages have been sent/received
        self._logger.info('Done!')

    def write_chunk_to_disk(self,dfc,workingdir,thread_lock=nullcontext) :
        """
        Add the data from a given file chunk to this file on disk in a given working directory
        dfc         = the DataFileChunk object whose data should be added
        workingdir  = path to the directory where the reconstructed files should be saved
        thread_lock = the lock object to acquire/release so that race conditions don't affect 
                      reconstruction of the files (optional, only needed if running this function asynchronously)
        """
        reconstructed_filepath = os.path.join(workingdir,dfc.filename)
        #lock the current thread while data is written to the file
        mode = 'r+b' if os.path.isfile(reconstructed_filepath) else 'w+b'
        with open(reconstructed_filepath,mode) as fp :
            with thread_lock :
                fp.seek(dfc.chunk_offset)
                fp.write(dfc.data)
                fp.flush()
                os.fsync(fp.fileno())
                fp.close()
        #add the offset of the added chunk to the set of reconstructed file chunks
        self._chunk_offsets_added_this_run.add(dfc.chunk_offset)
        #if this chunk was the last that needed to be added, check the hashes to make sure the file is the same as it was originally
        if len(self._chunk_offsets_added_this_run)==dfc.n_total_chunks :
            check_file_hash = sha512()
            with thread_lock :
                with open(reconstructed_filepath,'rb') as fp :
                    data = fp.read()
            check_file_hash.update(data)
            check_file_hash = check_file_hash.digest()
            if check_file_hash!=dfc.file_hash :
                return DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE
            else :
                return DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE
        else :
            return DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS
