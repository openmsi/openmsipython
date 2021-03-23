#imports
from .data_file_chunk import DataFileChunk
from ..my_kafka.my_producers import TutorialClusterProducer
from ..utilities.misc import populated_kwargs
from ..utilities.logging import Logger
from ..utilities.config import DATA_FILE_HANDLING_CONST, RUN_OPT_CONST, TUTORIAL_CLUSTER_CONST
from confluent_kafka import Producer
from queue import Queue
from threading import Thread, Lock
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
            self._logger = Logger()
        self._total_chunks = 0
        self._chunk_offsets_added_this_run = set()

    #################### PUBLIC FUNCTIONS ####################
    
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
        self._build_upload_queue(kwargs['chunk_size'])
        #upload all the objects in the queue in parallel threads
        upload_threads = []
        file_chunk = self._upload_queue.get()
        file_chunk_i = 0
        lock = Lock()
        while file_chunk is not None :
            file_chunk_i+=1
            t = Thread(target=file_chunk.upload_as_message,args=(file_chunk_i,
                                                                 self._total_chunks,
                                                                 kwargs['producer'],
                                                                 kwargs['topic_name'],
                                                                 self._logger,
                                                                 lock,))
            t.start()
            upload_threads.append(t)
            if len(upload_threads)>=kwargs['n_threads'] :
                for ut in upload_threads :
                    ut.join()
                upload_threads = []
            file_chunk = self._upload_queue.get()
        for ut in upload_threads :
            ut.join()
        self._logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
        kwargs['producer'].flush() #don't leave the function until every message has been sent/received
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

    #################### PRIVATE HELPER FUNCTIONS ####################

    #build the upload queue for this file path by breaking its binary data into chunks of the specified size
    def _build_upload_queue(self,chunk_size) :
        #start a hash for the file and the list of chunks
        file_hash = sha512()
        chunks = []
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
        self._total_chunks = len(chunks)
        file_hash = file_hash.digest()
        self._logger.info(f'File {self._filepath} has hash {file_hash}, with a total of {self._total_chunks} chunks')
        #add all the chunks to the upload queue
        self._upload_queue = Queue()
        for c in chunks:
            self._upload_queue.put(DataFileChunk(self._filepath,file_hash,c[0],c[1],c[2],self._filename,self._total_chunks))
        #add None to the queue as the final value
        self._upload_queue.put(None)
