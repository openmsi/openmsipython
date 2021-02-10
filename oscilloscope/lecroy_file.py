#imports
from ..utilities.logging import Logger
from ..config.oscilloscope import OSC_CONST
from queue import Queue
from threading import Thread, Lock
from hashlib import sha512
from argparse import ArgumentParser
import os, dataclasses, msgpack

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
        self._thread_lock = Lock()

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
        while token is not None :
            token_i+=1
            t = Thread(target=upload_lecroy_file_chunk_worker,args=(token,
                                                                    token_i,
                                                                    n_tokens,
                                                                    OSC_CONST.PRODUCER,
                                                                    OSC_CONST.LECROY_FILE_TOPIC_NAME,
                                                                    self._thread_lock,
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
        n_chunks = len(chunks)
        self._file_hash = file_hash.digest()
        self._logger.info(f'File {self._filepath} has hash {self._file_hash}, with a total of {n_chunks} chunks')
        #add all the chunks to the upload queue
        self._upload_queue = Queue()
        for c in chunks:
            self._upload_queue.put(LeCroyFileChunkInfo(self._filepath,self._file_hash,c[0],c[1],c[2],self._filename,n_chunks))
        self._upload_queue.put(None)

#################### UTILITY LeCroyFileChunkInfo CLASS ####################

@dataclasses.dataclass
class LeCroyFileChunkInfo :
    filepath : str
    file_hash : str
    chunk_hash : str
    chunk_offset : int
    chunk_size : int
    filename : str
    n_total_chunks : int

    #return the file chunk as a packed message
    def packed_as_msg_with_data(self,data) :
        p_list = []
        p_list.append(self.filepath)
        p_list.append(self.file_hash)
        p_list.append(self.chunk_hash)
        p_list.append(self.chunk_offset)
        p_list.append(data)
        p_list.append(self.filename)
        p_list.append(self.n_total_chunks)
        return msgpack.packb(p_list,use_bin_type=True)

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
    thread_lock.acquire()
    producer.produce(topic=topic_name,value=token.packed_as_msg_with_data(data))
    producer.poll(0)
    thread_lock.release()