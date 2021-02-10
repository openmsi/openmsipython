#imports
from ..utilities.oscilloscope import LeCroyFileChunkInfo, upload_lecroy_file_chunk_worker
from ..utilities.logging import Logger
from ..config.oscilloscope import OSC_CONST
from queue import Queue
from threading import Thread
from hashlib import sha512
from argparse import ArgumentParser
import os, math

# UploadLeCroyFile Class
class UploadLeCroyFile() :
    """
    Class for handling chunking and uploading of a single oscilloscope file to the LeCroy file topic of the LeCroy file cluster
    """
    def __init__(self,filepath,logger_to_use=None) :
        self._filepath = filepath
        self._filename = os.path.basename(filepath)
        if logger_to_use is None :
            logger_to_use = Logger()
        self._logger = logger_to_use
        self._producer = OSC_CONST.PRODUCER

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
                                                                    self._producer,
                                                                    OSC_CONST.LECROY_FILE_TOPIC_NAME,
                                                                    self._logger))
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

#################### MAIN SCRIPT HELPER FUNCTIONS ####################

#make sure the command line arguments are valid
def check_args(args,logger) :
    #the given file must exist
    if not os.path.isfile(args.filepath) :
        logger.error(f'ERROR: file {args.filepath} does not exist!',FileNotFoundError)
    #the chunk size has to be a nonzero power of two
    if args.chunk_size==0 or math.ceil(math.log2(args.chunk_size))!=math.floor(math.log2(args.chunk_size)) :
        logger.error(f'ERROR: chunk size {args.chunk_size} is invalid. Must be a (nonzero) power of two!',ValueError)

#################### MAIN SCRIPT ####################

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: filepath to upload
    parser.add_argument('filepath', help='Path to the file that should be uploaded')
    #optional arguments
    parser.add_argument('--n_threads', default=10, type=int,
                        help='Maximum number of threads to use (default=10)')
    parser.add_argument('--chunk_size', default=4096, type=int,
                        help='Size (in bytes) of chunks into which files should be broken as they are uploaded (default=4096)')
    args = parser.parse_args(args=args)
    #get the logger
    logger = Logger()
    #check the arguments
    check_args(args,logger)
    #make the UploadLeCroyFile for the single specified file
    upload_oscilloscope_file = UploadLeCroyFile(args.filepath,logger)
    #chunk and upload the file
    upload_oscilloscope_file.upload(args.n_threads,args.chunk_size)
    logger.info(f'Done uploading {args.filepath}')

if __name__=='__main__' :
    main()