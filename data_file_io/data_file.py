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

    #################### PROPERTIES ####################

    @property
    def filename(self): #the name of the file
        return self._filename
    @property
    def to_upload(self):
        return self._to_upload #whether or not this file will be considered when automatically uploading some group of data files
    @property
    def fully_enqueued(self): #whether or not this file has had all of its chunks added to an upload queue somewhere
        return self._fully_enqueued
    @property
    def upload_in_progress(self): #whether this file is in the process of being enqueued to be uploaded
        if (not self._to_upload) or self._fully_enqueued :
            return False
        return True
    @property
    def upload_status_msg(self): #a message stating the file's name and status w.r.t. being enqueued to be uploaded 
        msg = f'{self._filename} '
        if not self._to_upload :
            msg+='(will not be uploaded)'
        elif self._fully_enqueued :
            msg+='(fully enqueued)'
        elif len(self._chunks_to_upload)>0 :
            msg+='(in progress)'
        else :
            msg+='(waiting to be enqueued)'
        return msg

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,filepath,**kwargs) :
        """
        filepath = path to the file
        
        Possible keyword arguments:
        logger           = the logger object for this file's messages to use (a new one will be created if none is supplied)
        to_upload = if False, the file will be ignored for purposes of uploading to a topic (default is True)
        """
        self._filepath = filepath
        self._filename = os.path.basename(filepath)
        self._logger = kwargs.get('logger')
        if self._logger is None :
            self._logger = Logger(os.path.basename(__file__).split('.')[0])
        if kwargs.get('to_upload') is not None :
            self._to_upload = kwargs.get('to_upload')
        else :
            self._to_upload = True
        self._fully_enqueued = False
        self._chunks_to_upload = []
        self._chunk_offsets_downloaded = set()

    def add_chunks_to_upload_queue(self,queue,**kwargs) :
        """
        Add chunks of this file to a given upload queue. If the file runs out of chunks it will be marked as fully enqueued.

        Possible keyword arguments:
        n_threads  = the number of threads running during uploading; at most this number of chunks will be added per call to this function
                     if this argument isn't given, every chunk will be added
        chunk_size = the size of each file chunk in bytes (used to create the list of file chunks if it doesn't already exist)
                     the default value will be used if this argument isn't given
        """
        if self._fully_enqueued :
            self._logger.warning(f'WARNING: add_chunks_to_upload_queue called for fully enqueued file {self._filepath}, nothing else will be added.')
            return
        if len(self._chunks_to_upload)==0 :
            kwargs = populated_kwargs(kwargs,{'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE},self._logger)
            self._build_list_of_file_chunks(kwargs['chunk_size'])
        if kwargs.get('n_threads') is not None :
            n_chunks_to_add = kwargs['n_threads']
        else :
            n_chunks_to_add = len(self._chunks_to_upload)
        ic = 0
        while len(self._chunks_to_upload)>0 and ic<n_chunks_to_add :
            queue.put(self._chunks_to_upload.pop(0))
        if len(self._chunks_to_upload)==0 :
            self._fully_enqueued = True
    
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
        #add all the chunks to the upload queue
        upload_queue = Queue()
        self.add_chunks_to_upload_queue(upload_queue,chunk_size=kwargs['chunk_size'])
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
        self._chunk_offsets_downloaded.add(dfc.chunk_offset)
        #if this chunk was the last that needed to be added, check the hashes to make sure the file is the same as it was originally
        if len(self._chunk_offsets_downloaded)==dfc.n_total_chunks :
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

    #helper function to build the full list of DataFileChunks for this file given a chunk size (in bytes)
    def _build_list_of_file_chunks(self,chunk_size) :
        #start a hash for the file and the lists of chunks
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
        file_hash = file_hash.digest()
        self._logger.info(f'File {self._filepath} has a total of {len(chunks)} chunks')
        #add all the chunks to the final list as DataFileChunk objects
        for ic,c in enumerate(chunks,start=1) :
            self._chunks_to_upload.append(DataFileChunk(self._filepath,file_hash,c[0],c[1],c[2],self._filename,ic,len(chunks)))
