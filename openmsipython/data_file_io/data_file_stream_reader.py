#imports
from .utilities import 
from .config import RUN_OPT_CONST
from ..my_kafka.my_consumers import MyDeserializingConsumer
from ..utilities.controlled_process import ControlledProcessMultiThreaded
from ..utilities.logging import Logger
from ..utilities.my_base_class import MyBaseClass
from queue import Queue
from threading import Thread
import uuid

class DataFileStreamReader(ControlledProcessMultiThreaded,MyBaseClass) :
    """
    A class to read DataFileChunk messages from a topic and do something with them
    """

    #################### PROPERTIES ####################

    @property
    def topic_name(self) :
        return self.__topic_name
    @property
    def logger(self) :
        return self.__logger
    @property
    def n_msgs_read(self) :
        return self.__n_msgs_read
    @property
    def message_queue(self) :
        return self.__message_queue

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,config_path,topic_name,*args,
                 consumer_group_ID=str(uuid.uuid1()),
                 max_queue_size=RUN_OPT_CONST.DEFAULT_MAX_MESSAGE_QUEUE_SIZE,
                 **other_kwargs) :
        """
        arguments:
        config_path = path to the config file that should be used to define the consumer group
        topic_name  = name of the topic to consume messages from

        keyword arguments:
        consumer_group_id = ID to use for all consumers in the group (a new & unique ID is created by default)
        max_queue_size = the maximum number of messages allowed to be waiting in the internal queue at a given time

        possible other keyword arguments: 
        logger = the logger object to use (a new one will be created if none is supplied)
        n_threads = gets passed along to ControlledProcessMultithreaded
        """
        super().__init__(*args,**other_kwargs)
        self.__topic_name = topic_name
        self.__n_msgs_read = 0
        self.__logger = other_kwargs.get('logger')
        if self.__logger is None :
            self.__logger = Logger(pathlib.Path(__file__).name.split('.')[0])
        #start up the message queue
        self.__message_queue = Queue(max_queue_size)
        #create a Consumer for each thread and subscribe it to the topic
        self.__consumers = []
        for i in range(self.n_threads) :
            #start up a consumer
            consumer = MyDeserializingConsumer.from_file(config_path,logger=self.__logger,group_id=consumer_group_id)
            consumer.subscribe([self.__topic_name])
            self.__consumers.append(consumer)
        
    def run(self) :
        super().run(self.__consumers)

    #################### PRIVATE HELPER FUNCTIONS ####################

    def _run_worker(self,consumer) :
        """
        Consume messages from the topic, and add them to the DataFileStreamReader queue
        Several iterations of this function are meant to run in parallel threads, working with a group of Consumers.
        """
        while self.alive :
            try :
                consumed_msg = consumer.poll(0)
            except Exception as e :
                self.logger.warning(f'WARNING: encountered an error in a call to consumer.poll() and will skip the offending message. Error: {e}')
                continue
            if consumed_msg is not None and consumed_msg.error() is None :
                self.__message_queue.put(consumed_msg.value())
