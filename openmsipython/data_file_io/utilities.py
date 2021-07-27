#Several utility functions

def produce_from_queue_of_file_chunks(queue,producer,topic_name,logger) :
    """
    produce every file chunk in a given queue to the given topic using the given producer
    """
    file_chunk = queue.get()
    while file_chunk is not None :
        file_chunk.produce_to_topic(producer,topic_name,logger)
        queue.task_done()
        file_chunk = queue.get()
    queue.task_done()

#a very small class (and instance thereof) to hold a logger object to use in the producer callback 
# (literally exists because I don't think I can add extra keyword or other arguments to the producer callback function)
class ProducerCallbackLogger :

    @property
    def logger(self) :
        return self._logger
    @logger.setter
    def logger(self,logger_val) :
        self._logger = logger_val
    def __init__(self) :
        self._logger = None

PRODUCER_CALLBACK_LOGGER = ProducerCallbackLogger()

#a callback function to use for testing whether a message has been successfully produced to the topic
def producer_callback(err,msg) :
    global PRODUCER_CALLBACK_LOGGER
    if err is not None: #raise an error if the message wasn't sent successfully
        if err.fatal() :
            logmsg=f'ERROR: fatally failed to deliver message with key {msg.key()}. Error reason: {err.str()}'
            if PRODUCER_CALLBACK_LOGGER.logger is not None :
                PRODUCER_CALLBACK_LOGGER.logger.error(logmsg,RuntimeError)
            else :
                raise RuntimeError(logmsg)
        elif not err.retriable() :
            logmsg=f'ERROR: Failed to deliver message with key {msg.key()} and cannot retry. Error reason: {err.str()}'
            if PRODUCER_CALLBACK_LOGGER.logger is not None :
                PRODUCER_CALLBACK_LOGGER.logger.error(logmsg,RuntimeError)
            else :
                raise RuntimeError(logmsg)