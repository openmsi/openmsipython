#imports
from .data_file_chunk import DataFileChunk
from .utilities import produce_from_queue_of_file_chunks
from .config import DATA_FILE_HANDLING_CONST, RUN_OPT_CONST
from ..my_kafka.my_producers import MySerializingProducer
from ..utilities.misc import populated_kwargs
from ..utilities.logging import Logger
from ..utilities.my_base_class import MyBaseClass
from abc import ABC, abstractmethod
from threading import Thread, Lock
from queue import Queue
from contextlib import nullcontext
from hashlib import sha512
import pathlib, os

class DataFile(MyBaseClass) :
    """
    Base class for representing a single data file
    """

    #################### PROPERTIES ####################

    @property
    def filepath(self):
        return self.__filepath
    @property
    def filename(self):
        return self.__filename
    @property
    def logger(self):
        return self.__logger

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,filepath,**kwargs) :
        """
        filepath = path to the file
        
        Possible keyword arguments:
        logger    = the logger object for this file's messages to use (a new one will be created if none is supplied)
        """
        self.__filepath = filepath.resolve()
        self.__filename = self.__filepath.name
        self.__logger = kwargs.get('logger')
        if self.__logger is None :
            self.__logger = Logger(pathlib.Path(__file__).name.split('.')[0])

class UploadDataFile(DataFile) :
    """
    Class to represent a data file whose messages will be uploaded to a topic
    """

    #################### PROPERTIES ####################

    @property
    def select_bytes(self) :
        return []   # in child classes this can be a list of tuples of (start_byte,stop_byte) 
                    # in the file that will be the only ranges of bytes added when creating the list of chunks
    @property
    def rootdir(self) :
        return self.__rootdir
    @property
    def chunks_to_upload(self) :
        return self.__chunks_to_upload
    @property
    def to_upload(self):
        return self.__to_upload #whether or not this file will be considered when automatically uploading some group of data files
    @property
    def fully_enqueued(self): #whether or not this file has had all of its chunks added to an upload queue somewhere
        return self.__fully_enqueued
    @property
    def waiting_to_upload(self): #whether or not this file is waiting for its upload to begin
        if (not self.__to_upload) or self.__fully_enqueued :
            return False
        if len(self.__chunks_to_upload)>0 :
            return False
        return True
    @property
    def upload_in_progress(self): #whether this file is in the process of being enqueued to be uploaded
        if (not self.__to_upload) or self.__fully_enqueued :
            return False
        if len(self.__chunks_to_upload)==0 :
            return False
        return True
    @property
    def upload_status_msg(self): #a message stating the file's name and status w.r.t. being enqueued to be uploaded 
        if self.__rootdir is None :
            msg = f'{self.filepath} '
        else :
            msg = f'{self.filepath.relative_to(self.__rootdir)} '
        if not self.__to_upload :
            msg+='(will not be uploaded)'
        elif self.__fully_enqueued :
            msg+='(fully enqueued)'
        elif self.upload_in_progress :
            msg+='(in progress)'
        elif self.waiting_to_upload :
            msg+='(waiting to be enqueued)'
        else :
            msg+='(status unknown)'
        return msg

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,*args,to_upload=True,rootdir=None,**kwargs) :
        """
        to_upload = if False, the file will be ignored for purposes of uploading to a topic (default is True)
        rootdir = path to the "root" directory that this file is in; anything in the path beyond this root directory 
                  will be added to the DataFileChunk so that it will be reconstructed inside a subdirectory
        """
        super().__init__(*args,**kwargs)
        self.__to_upload = to_upload
        if rootdir is None :
            self.__rootdir = self.filepath.parent
        else :
            self.__rootdir = rootdir
        self.__fully_enqueued = False
        self.__chunks_to_upload = []

    def add_chunks_to_upload_queue(self,queue,**kwargs) :
        """
        Add chunks of this file to a given upload queue. If the file runs out of chunks it will be marked as fully enqueued.
        If the given queue is full this function will do absolutely nothing and will just return.

        Possible keyword arguments:
        n_threads  = the number of threads running during uploading; at most 5*this number of chunks will be added per call to this function
                     if this argument isn't given, every chunk will be added
        chunk_size = the size of each file chunk in bytes (used to create the list of file chunks if it doesn't already exist)
                     the default value will be used if this argument isn't given
        """
        if self.__fully_enqueued :
            self.logger.warning(f'WARNING: add_chunks_to_upload_queue called for fully enqueued file {self.filepath}, nothing else will be added.')
            return
        if queue.full() :
            return
        if len(self.__chunks_to_upload)==0 :
            kwargs = populated_kwargs(kwargs,{'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE},self.logger)
            self._build_list_of_file_chunks(kwargs['chunk_size'])
        if kwargs.get('n_threads') is not None :
            n_chunks_to_add = 5*kwargs['n_threads']
        else :
            n_chunks_to_add = len(self.__chunks_to_upload)
        ic = 0
        while len(self.__chunks_to_upload)>0 and ic<n_chunks_to_add :
            queue.put(self.__chunks_to_upload.pop(0))
            ic+=1
        if len(self.__chunks_to_upload)==0 :
            self.__fully_enqueued = True
    
    def upload_whole_file(self,config_path,topic_name,**kwargs) :
        """
        Chunk and upload an entire file on disk to a cluster's topic.

        config_path = path to the config file to use in defining the producer
        topic_name  = name of the topic to produce messages to
        
        Possible keyword arguments:
        n_threads  = the number of threads to run at once during uploading
        chunk_size = the size of each file chunk in bytes
        """
        #set the important variables
        kwargs = populated_kwargs(kwargs,
                                  {'n_threads': RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                   'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                  },self.logger)
        #start the producer
        producer = MySerializingProducer.from_file(config_path,logger=self.logger)
        startup_msg = f"Uploading entire file {self.filepath} to {topic_name} in {kwargs['chunk_size']} byte chunks "
        startup_msg+=f"using {kwargs['n_threads']} threads...."
        self.logger.info(startup_msg)
        #add all the chunks to the upload queue
        upload_queue = Queue()
        self.add_chunks_to_upload_queue(upload_queue,chunk_size=kwargs['chunk_size'])
        #add "None" to the queue for each thread as the final values
        for ti in range(kwargs['n_threads']) :
            upload_queue.put(None)
        #produce all the messages in the queue using multiple threads
        upload_threads = []
        for ti in range(kwargs['n_threads']) :
            t = Thread(target=produce_from_queue_of_file_chunks, args=(upload_queue,
                                                                       producer,
                                                                       topic_name,
                                                                       self.logger))
            t.start()
            upload_threads.append(t)
        #join the threads
        for ut in upload_threads :
            ut.join()
        self.logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
        producer.flush() #don't leave the function until all messages have been sent/received
        self.logger.info('Done!')

    #################### PRIVATE HELPER FUNCTIONS ####################

    def _build_list_of_file_chunks(self,chunk_size) :
        """
        Build the full list of DataFileChunks for this file given a chunk size (in bytes)
        """
        #first make sure the choices of select_bytes are valid if necessary and sort them by their start byte to keep the file hash in order
        if self.select_bytes!=[] :
            if type(self.select_bytes)!=list :
                raise ValueError(f'ERROR: select_bytes={self.select_bytes} but is expected to be a list!')
            for sbt in self.select_bytes :
                if type(sbt)!=tuple or len(sbt)!=2 :
                    raise ValueError(f'ERROR: found {sbt} in select_bytes but all elements are expected to be two-entry tuples!')
                elif sbt[0]>=sbt[1] :
                    raise ValueError(f'ERROR: found {sbt} in select_bytes but start byte cannot be >= stop byte!')
            sorted_select_bytes = sorted(self.select_bytes,key=lambda x: x[0])
        #start a hash for the file and the lists of chunks
        file_hash = sha512()
        chunks = []
        isb = 0 #index for the current sorted_select_bytes entry if necessary
        #read the binary data in the file as chunks of the given size, adding each chunk to the list 
        with open(self.filepath,'rb') as fp :
            chunk_offset = 0
            file_offset = 0 if self.select_bytes==[] else sorted_select_bytes[isb][0]
            n_bytes_to_read = chunk_size if self.select_bytes==[] else min(chunk_size,sorted_select_bytes[isb][1]-file_offset)
            chunk = fp.read(chunk_size)
            while len(chunk) > 0 :
                file_hash.update(chunk)
                chunk_hash = sha512()
                chunk_hash.update(chunk)
                chunk_hash = chunk_hash.digest()
                chunk_length = len(chunk)
                chunks.append([chunk_hash,file_offset,chunk_length])
                chunk_offset += chunk_length
                file_offset += chunk_length
                if self.select_bytes!=[] and file_offset==sorted_select_bytes[isb][1] :
                    isb+=1
                    if isb>(len(sorted_select_bytes)-1) :
                        break
                    file_offset=sorted_select_bytes[isb][0]
                n_bytes_to_read = chunk_size if self.select_bytes==[] else min(chunk_size,sorted_select_bytes[isb][1]-file_offset)
                chunk = fp.read(chunk_size)
        file_hash = file_hash.digest()
        self.logger.info(f'File {self.filepath} has a total of {len(chunks)} chunks')
        #add all the chunks to the final list as DataFileChunk objects
        for ic,c in enumerate(chunks,start=1) :
            self.__chunks_to_upload.append(DataFileChunk(self.filepath,self.filename,file_hash,c[0],c[1],c[2],ic,len(chunks),rootdir=self.__rootdir))

class DownloadDataFile(DataFile,ABC) :
    """
    Class to represent a data file that will be read as messages from a topic
    """

    @property
    @abstractmethod
    def check_file_hash(self) :
        pass #the hash of the data in the file after it was read; not implemented in the base class

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        #start an empty set of this file's downloaded offsets
        self._chunk_offsets_downloaded = set()
        #a thread lock to guarantee that only one thread does certain critical things to the file at once

    def add_chunk(self,dfc,thread_lock=nullcontext(),*args,**kwargs) :
        """
        A function to process a chunk that's been read from a topic
        Returns a number of codes based on what effect adding the chunk had
        
        This function calls _on_add_chunk, 
        
        dfc = the DataFileChunk object whose data should be added
        thread_lock = the lock object to acquire/release so that race conditions don't affect 
                      reconstruction of the files (optional, only needed if running this function asynchronously)
        """
        #the filepath of this DownloadDataFile and of the given DataFileChunk must match
        if dfc.filepath!=self.filepath :
            self.logger.error(f'ERROR: filepath mismatch between data file chunk {dfc._filepath} and data file {self.filepath}',ValueError)
        #if this chunk's offset has already been written to disk, return the "already written" code
        if dfc.chunk_offset in self._chunk_offsets_downloaded :
            return DATA_FILE_HANDLING_CONST.CHUNK_ALREADY_WRITTEN_CODE
        #acquire the thread lock to make sure this process is the only one dealing with this particular file
        with thread_lock:
            #call the function to actually add the chunk
            self._on_add_chunk(dfc,*args,**kwargs)
            #add the offset of the added chunk to the set of reconstructed file chunks
            self._chunk_offsets_downloaded.add(dfc.chunk_offset)
            #if this chunk was the last that needed to be added, check the hashes to make sure the file is the same as it was originally
            if len(self._chunk_offsets_downloaded)==dfc.n_total_chunks :
                if self.check_file_hash!=dfc.file_hash :
                    return DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE
                else :
                    return DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE
            else :
                return DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS

    @abstractmethod
    def _on_add_chunk(dfc,*args,**kwargs) :
        """
        A function to actually process a new chunk being added to the file
        This function is executed while a thread lock is acquired so it will never run asynchronously
        Also any DataFileChunks passed to this function are guaranteed to have unique offsets
        Not implemented in the base class
        """
        pass

class DownloadDataFileToDisk(DownloadDataFile) :
    """
    Class to represent a data file that will be reconstructed on disk using messages read from a topic
    """

    @property
    def check_file_hash(self) :
        check_file_hash = sha512()
        with open(self._filepath,'rb') as fp :
            data = fp.read()
        check_file_hash.update(data)
        return check_file_hash.digest()

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        #create the parent directory of the file if it doesn't exist yet (in case the file is in a new subdirectory)
        if not self.filepath.parent.is_dir() :
            self.filepath.parent.mkdir(parents=True)

    def _on_add_chunk(self,dfc) :
        """
        Add the data from a given file chunk to this file on disk
        """
        mode = 'r+b' if self.filepath.is_file() else 'w+b'
        with open(self.filepath,mode) as fp :
            fp.seek(dfc.chunk_offset)
            fp.write(dfc.data)
            fp.flush()
            os.fsync(fp.fileno())
            fp.close()

class DownloadDataFileToMemory(DownloadDataFile) :
    """
    Class to represent a data file that will be held in memory and populated by the contents of messages from a topic
    """

    @property
    def bytestring(self) :
        if self.__bytestring is None :
            self.__create_bytestring()
        return self.__bytestring
    @property
    def check_file_hash(self) :
        check_file_hash = sha512()
        check_file_hash.update(self.bytestring)
        return check_file_hash.digest()

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        #start a dictionary of the file data by their offsets
        self.__chunk_data_by_offset = {}
        #placeholder for the eventual full data bytestring
        self.__bytestring = None

    def _on_add_chunk(self,dfc) :
        """
        Add the data from a given file chunk to the dictionary of data by offset
        """
        self.__chunk_data_by_offset[dfc.chunk_offset] = dfc.data

    def __create_bytestring(self) :
        """
        Makes all of the data held in the dictionary into a single bytestring ordered by offset of each chunk
        """
        bytestring = b''
        for data in [self.__chunk_data_by_offset[offset] for offset in sorted(self.__chunk_data_by_offset.keys())] :
            bytestring+=data
        self.__bytestring = bytestring
