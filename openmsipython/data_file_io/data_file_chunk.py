#imports
from .utilities import producer_callback, PRODUCER_CALLBACK_LOGGER
from ..utilities.logging import Logger
from hashlib import sha512
import time, pathlib

# DataFileChunk Class 
class DataFileChunk() :
    """
    Class to deal with single chunks of file info
    """

    #################### SPECIAL FUNCTIONS ####################

    def __init__(self,filepath,filename,file_hash,chunk_hash,chunk_offset,chunk_size,chunk_i,n_total_chunks,data=None) :
        """
        filepath       = path to this chunk's original file
        filename       = the name of the file (important to pass for compatibility btwn. filesystems)
        file_hash      = hash of this chunk's entire file data
        chunk_hash     = hash of this chunk's data
        chunk_offset   = offset (in bytes) of this chunk within the original file
        chunk_size     = size of this chunk (in bytes)
        chunk_i        = index of this chunk within the larger file
        n_total_chunks = the total number of chunks to expect from the original file
        data           = the actual binary data of this chunk of the file (can be set later if this chunk is being produced and not consumed)
        """
        self.filepath = filepath
        self.filename = filename
        self.file_hash = file_hash
        self.chunk_hash = chunk_hash
        self.chunk_offset = chunk_offset
        self.chunk_size = chunk_size
        self.chunk_i = chunk_i
        self.n_total_chunks = n_total_chunks
        self.data = data

    def __eq__(self,other) :
        if not isinstance(other,DataFileChunk) :
            return NotImplemented
        retval = True
        #retval = retval and self.filepath == other.filepath #chunks can have different filepaths if created on different machines but still be equal
        retval = retval and self.filename == other.filename
        retval = retval and self.file_hash == other.file_hash
        retval = retval and self.chunk_hash == other.chunk_hash
        retval = retval and self.chunk_offset == other.chunk_offset
        retval = retval and self.chunk_size == other.chunk_size
        retval = retval and self.chunk_i == other.chunk_i
        retval = retval and self.n_total_chunks == other.n_total_chunks
        retval = retval and self.data == other.data
        return retval

    #################### PUBLIC FUNCTIONS ####################

    def produce_to_topic(self,producer,topic_name,logger,print_every=1000) :
        """
        Upload the file chunk as a message to the specified topic using the specified SerializingProducer
        Meant to be run in parallel
        producer     = the producer to use
        topic_name   = the name of the topic to produce the message to
        logger       = the logger object to use
        print_every  = how often to print/log progress messages
        """
        #set the logger so the callback can use it
        PRODUCER_CALLBACK_LOGGER.logger = logger
        #log a line about this file chunk if applicable
        if (self.chunk_i-1)%print_every==0 or self.chunk_i==self.n_total_chunks :
            logger.info(f'uploading {self.filepath} chunk {self.chunk_i} (out of {self.n_total_chunks})')
        #get this chunk's data from the file if necessary
        if self.data is None :
            self._populate_with_file_data(logger)
        #produce the message to the topic
        message_key = f'{self.filename}_chunk_{self.chunk_i}_of_{self.n_total_chunks}'
        success=False; retries=0; sleep_secs=5; total_wait_secs=60 
        if (not success) and retries<(1.0*total_wait_secs/sleep_secs) :
            try :
                producer.produce(topic=topic_name,key=message_key,value=self,on_delivery=producer_callback)
                success=True
            except BufferError :
                time.sleep(sleep_secs)
                retries+=1
        if not success :
            logger.warning(f'WARNING: message with key {message_key} failed to buffer for more than {total_wait_secs}s and was dropped!')
        producer.poll(0.025)

    #################### PRIVATE HELPER FUNCTIONS ####################

    #populate this chunk with the actual data from the file
    def _populate_with_file_data(self,logger=None) :
        #create a new logger if one isn't given
        if logger is None :
            logger = Logger(pathlib.Path(__file__).name.split('.')[0])
        #get the data from the file
        with open(self.filepath, "rb") as fp:
            fp.seek(self.chunk_offset)
            data = fp.read(self.chunk_size)
        #make sure it's of the expected size
        if len(data) != self.chunk_size:
            msg = f'ERROR: chunk {self.chunk_hash} size {len(data)} != expected size {self.chunk_size} in file {self.filepath}, offset {self.chunk_offset}'
            logger.error(msg,ValueError)
        #check that its hash matches what was found at the time of putting it in the queue
        check_chunk_hash = sha512()
        check_chunk_hash.update(data)
        check_chunk_hash = check_chunk_hash.digest()
        if self.chunk_hash != check_chunk_hash:
            msg = f'ERROR: chunk hash {check_chunk_hash} != expected hash {self.chunk_hash} in file {self.filepath}, offset {self.chunk_offset}'
            logger.error(msg,ValueError)
        #set the chunk's data value
        self.data = data
