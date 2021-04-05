#imports
from hashlib import sha512
import msgpack, time

# DataFileChunk Class 
class DataFileChunk() :
    """
    Class to deal with single chunks of file info
    """
    def __init__(self,*args) :
        """
        *args = ordered list of initializing arguments (see assignments below for what exactly they are)
        """
        self.filepath = args[0]
        self.file_hash = args[1]
        self.chunk_hash = args[2]
        self.chunk_offset = args[3]
        self.chunk_size = args[4]
        self.filename = args[5]
        self.chunk_i = args[6]
        self.n_total_chunks = args[7]
        if len(args)>8 :
            self.data = args[8]
        else :
            self.data=None

    #class method to instantiate the object by reading a token instead of from individual values
    @classmethod
    def from_token(cls,token,**kwargs) :
        """
        Possible keyword arguments:
        logger = the logger object to use
        """
        logger = kwargs.get('logger')
        p_list = msgpack.unpackb(token,raw=True)
        if len(p_list)!=8 :
            msg = f'ERROR: unrecognized token passed to DataFileChunk.from_token(). Expected 8 properties but found {len(p_list)}'
            if logger is None :
                raise ValueError(msg)
            else :
                logger.error(msg,ValueError)
        args = [None,None,None,None,None,None,None,None,None]
        try :
            args[0] = str(p_list[0].decode())
            args[1] = p_list[1]
            chunk_hash = p_list[2]
            args[2] = chunk_hash
            chunk_offset = int(p_list[3])
            args[3] = chunk_offset
            data = p_list[4]
            args[8] = data
            args[4] = len(data)
            filename = str(p_list[5].decode())
            args[5] = filename
            args[6] = int(p_list[6])
            args[7] = int(p_list[7])
        except Exception as e :
            raise ValueError(f'ERROR: unrecognized value(s) when instantiating DataFileChunk from token. Exception: {e}')
        check_chunk_hash = sha512()
        check_chunk_hash.update(data)
        check_chunk_hash = check_chunk_hash.digest()
        if check_chunk_hash!=chunk_hash :
            msg = f'ERROR: chunk hash {check_chunk_hash} != expected hash {chunk_hash} in file {filename}, offset {chunk_offset}'
            if logger is None :
                raise ValueError(msg)
            else :
                logger.error(msg,ValueError)
        return cls(*args)

    #################### PUBLIC FUNCTIONS ####################

    def upload_as_message(self,producer,topic_name,logger,thread_lock,print_every=1000) :
        """
        Upload the file chunk as a message to the specified topic using the specified producer
        Meant to be run in parallel
        producer     = the producer to use
        topic_name   = the name of the topic to produce the message to
        logger       = the logger object to use
        thread_lock  = a lock to acquire and release when logging messages to keep everything clean
        print_every  = how often to print/log progress messages
        """
        #set the logger so the callback can use it
        global LOGGER
        LOGGER = logger
        #log a line about this file chunk if applicable
        filepath = self.filepath
        if (self.chunk_i-1)%print_every==0 or self.chunk_i==self.n_total_chunks :
            with thread_lock :
                logger.info(f'uploading {filepath} chunk {self.chunk_i} (out of {self.n_total_chunks})')
        #get this chunk's data from the file
        with open(filepath, "rb") as fp:
            fp.seek(self.chunk_offset)
            data = fp.read(self.chunk_size)
        #make sure it's of the expected size
        if len(data) != self.chunk_size:
            with thread_lock :
                msg = f'ERROR: chunk {self.chunk_hash} size {len(data)} != expected size {self.chunk_size} in file {filepath}, offset {self.chunk_offset}'
                logger.error(msg,ValueError)
        #check that its hash matches what was found at the time of putting it in the queue
        check_chunk_hash = sha512()
        check_chunk_hash.update(data)
        check_chunk_hash = check_chunk_hash.digest()
        if self.chunk_hash != check_chunk_hash:
            with thread_lock :
                msg = f'ERROR: chunk hash {check_chunk_hash} != expected hash {self.chunk_hash} in file {filepath}, offset {self.chunk_offset}'
                logger.error(msg,ValueError)
        #produce the message to the topic
        message_value = self._packed_as_message(data)
        with thread_lock :
            try :
                producer.produce(topic=topic_name,
                                 key=f'{self.filename}_chunk_{self.chunk_i}_of_{self.n_total_chunks}',
                                 value=message_value,callback=producer_callback)
            except BufferError :
                logger.info(f'Flushing producer to empty local buffer queue (this may take a moment)...')
                producer.flush()
                logger.info(f'Done flushing producer.')
                producer.produce(topic=topic_name,
                                 key=f'{self.filename}_chunk_{self.chunk_i}_of_{self.n_total_chunks}',
                                 value=message_value,callback=producer_callback)
        producer.poll(0.05)


    #################### PRIVATE HELPER FUNCTIONS ####################

    #helper function to return the file chunk as a packed message given the actual data from the file
    def _packed_as_message(self,data) :
        p_list = []
        p_list.append(self.filepath)
        p_list.append(self.file_hash)
        p_list.append(self.chunk_hash)
        p_list.append(self.chunk_offset)
        p_list.append(data)
        p_list.append(self.filename)
        p_list.append(self.chunk_i)
        p_list.append(self.n_total_chunks)
        return msgpack.packb(p_list,use_bin_type=True)

#################### FILE-SCOPE VARIABLES AND HELPER FUNCTIONS ####################

#logger for use with the producer callback 
LOGGER=None

#a callback function to use for testing whether a message has been successfully produced to the topic
def producer_callback(err,msg) :
    global LOGGER
    if err is not None: #raise an error if the message wasn't sent successfully
        if err.fatal() :
            logmsg=f'ERROR: fatally failed to deliver message with key {msg.key()}. Error reason: {err.str()}'
            if LOGGER is not None :
                LOGGER.error(logmsg,RuntimeError)
            else :
                raise RuntimeError(logmsg)
        elif not err.retriable() :
            logmsg=f'WARNING: Failed to deliver message with key {msg.key()}. Error reason: {err.str()}'
            if LOGGER is not None :
                LOGGER.warning(logmsg)
            else :
                print(logmsg)

