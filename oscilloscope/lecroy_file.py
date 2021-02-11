#imports
from ..utilities.logging import Logger
from ..config.oscilloscope import OSC_CONST
from queue import Queue
from threading import Thread, Lock
from hashlib import sha512
from argparse import ArgumentParser
import os, msgpack

# LeCroyFile Class
class LeCroyFile() :
    """
    Class for handling chunking and uploading of a single oscilloscope file to the LeCroy file topic of the LeCroy file cluster
    """
    def __init__(self,filepath,logger_to_use=None) :
        self._filepath = filepath
        self._filename = os.path.basename(filepath)
        if logger_to_use is None :
            logger_to_use = Logger()
        self._logger = logger_to_use
        self._chunks_added = 0
        self._total_chunks = 0

    #################### PUBLIC FUNCTIONS ####################
    
    def upload(self,n_threads,chunk_size) :
        """
        Chunk and upload the file to the oscilloscope cluster topic.
        n_threads  = the number of threads to run at once during uploading
        chunk_size = the size of each file chunk in bytes
        """
        self._logger.info(f'Uploading file {self._filepath}....')
        #build the upload queue
        self._build_upload_queue(chunk_size)
        #upload all the objects in the queue in parallel threads
        n_tokens = self._upload_queue.qsize()
        upload_threads = []
        token = self._upload_queue.get()
        token_i = 0
        lock = Lock()
        while token is not None :
            token_i+=1
            t = Thread(target=upload_lecroy_file_chunk_worker,args=(token,
                                                                    token_i,
                                                                    n_tokens,
                                                                    OSC_CONST.PRODUCER,
                                                                    OSC_CONST.LECROY_FILE_TOPIC_NAME,
                                                                    lock,
                                                                    self._logger,))
            t.start()
            upload_threads.append(t)
            if len(upload_threads)>=n_threads :
                for ut in upload_threads :
                    ut.join()
                upload_threads = []
            token = self._upload_queue.get()
        for ut in upload_threads :
            ut.join()

    def add_file_chunk(self,fci,workingdir) :
        """
        Add the data from a given file chunk to this file on disk in a given working directory
        fci = the LeCroyFileChunkInfo object whose data should be added
        workingdir = path to the directory where the reconstructed files should be saved
        """
        reconstructed_filepath = os.path.join(workingdir,fci.filename)
        #lock the current thread while data is written to the file
        mode = 'r+b' if os.path.isfile(reconstructed_filepath) else 'w+b'
        with open(reconstructed_filepath,mode) as fp :
            fp.seek(fci.chunk_offset)
            fp.write(fci.data)
        #increment how many chunks have been added to this file
        self._chunks_added+=1
        #if this chunk was the last that needed to be added, check the hashes to make sure the file is the same as it was originally
        if self._chunks_added==fci.n_total_chunks :
            check_file_hash = sha512()
            with open(reconstructed_filepath,'rb') as fp :
                data = fp.read()
            check_file_hash.update(data)
            check_file_hash = check_file_hash.digest()
            if check_file_hash!=fci.file_hash :
                return OSC_CONST.FILE_HASH_MISMATCH_CODE
            else :
                return OSC_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE
        else :
            return OSC_CONST.FILE_IN_PROGRESS

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
            self._upload_queue.put(LeCroyFileChunkInfo(self._filepath,file_hash,c[0],c[1],c[2],self._filename,self._total_chunks))
        self._upload_queue.put(None)

# LeCroyFileChunkInfo Class 
class LeCroyFileChunkInfo() :
    """
    Class to deal with single chunks of file info
    """
    def __init__(self,*args) :
        """
        *args = list of initializing arguments
        if len(args) is 7, the object can be instantiated from those values
        if len(args) is 1 instead, then that argument is assumed to be a token to be unpacked
        """
        if len(args)==7 :
            self.filepath = args[0]
            self.file_hash = args[1]
            self.chunk_hash = args[2]
            self.chunk_offset = args[3]
            self.chunk_size = args[4]
            self.filename = args[5]
            self.n_total_chunks = args[6]
            self.data = None
        elif len(args)==1 :
            self._init_from_token(args[0])
        else :
            msg = f'ERROR: {len(args)} arguments given to LeCroyFileChunkInfo, but this object must be '
            msg+= 'instantiated using either 7 specific arguments or a single token.'
            raise ValueError(msg)

    #################### PUBLIC FUNCTIONS ####################

    def packed_as_msg_with_data(self,data) :
        """
        return the file chunk as a packed message
        data = binary data from the file associated with this chunk
        """
        p_list = []
        p_list.append(self.filepath)
        p_list.append(self.file_hash)
        p_list.append(self.chunk_hash)
        p_list.append(self.chunk_offset)
        p_list.append(data)
        p_list.append(self.filename)
        p_list.append(self.n_total_chunks)
        return msgpack.packb(p_list,use_bin_type=True)

    #################### PRIVATE HELPER FUNCTIONS ####################

    #helper function to instantiate the object by reading a token instead of from individual values
    def _init_from_token(self,token) :
        p_list = msgpack.unpackb(token,raw=True)
        if len(p_list)!=7 :
            raise ValueError(f'ERROR: unrecognized token passed to LeCroyFileChunkInfo. Expected 7 properties but found {len(p_list)}')
        else :
            try :
                self.filepath = str(p_list[0].decode())
                self.file_hash = p_list[1]
                self.chunk_hash = p_list[2]
                self.chunk_offset = int(p_list[3])
                self.data = p_list[4]
                self.chunk_size = len(self.data)
                self.filename = str(p_list[5].decode())
                self.n_total_chunks = int(p_list[6])
            except Exception as e :
                raise ValueError(f'ERROR: unrecognized value(s) when instantiating LeCroyFileChunkInfo from token. Exception: {e}')
        if len(self.data)!=self.chunk_size :
            msg = f'ERROR: chunk {self.chunk_hash} size {len(self._data)} != expected size {self.chunk_size} in file {self.filename}, offset {self.chunk_offset}'
            raise ValueError(msg)
        check_chunk_hash = sha512()
        check_chunk_hash.update(self.data)
        check_chunk_hash = check_chunk_hash.digest()
        if check_chunk_hash!=self.chunk_hash :
            msg = f'ERROR: chunk hash {check_chunk_hash} != expected hash {self.chunk_hash} in file {self.filename}, offset {self.chunk_offset}'
            raise ValueError(msg)

#################### FILE-SCOPE HELPER FUNCTIONS ####################

#upload a single LeCroyFileChunkInfo token with its data to a given topic (meant to be run in parallel)
def upload_lecroy_file_chunk_worker(token,token_i,n_tokens,producer,topic_name,thread_lock,logger=None,print_every=1000) :
    if logger is None :
        logger = Logger()
    filepath = token.filepath
    if (token_i-1)%print_every==0 :
        logger.info(f'uploading {filepath} chunk {token_i} (out of {n_tokens})')
    chunk_hash = token.chunk_hash
    chunk_offset = token.chunk_offset
    chunk_len = token.chunk_size
    #get this chunk's data from the file
    with open(filepath, "rb") as fp:
        fp.seek(chunk_offset)
        data = fp.read(chunk_len)
    #make sure it's of the expected size
    if len(data) != chunk_len:
        msg = f'ERROR: chunk {chunk_hash} size {len(data)} != expected size {chunk_len} in file {filepath}, offset {chunk_offset}'
        logger.error(msg,ValueError)
    check_chunk_hash = sha512()
    check_chunk_hash.update(data)
    check_chunk_hash = check_chunk_hash.digest()
    if chunk_hash != check_chunk_hash:
        msg = f'ERROR: chunk hash {check_chunk_hash} != expected hash {chunk_hash} in file {filepath}, offset {chunk_offset}'
        logger.error(msg,ValueError)
    with thread_lock :
        producer.produce(topic=topic_name,value=token.packed_as_msg_with_data(data))
        producer.poll(0)
