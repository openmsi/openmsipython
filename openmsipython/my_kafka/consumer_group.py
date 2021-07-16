#imports
from .my_consumers import MyDeserializingConsumer
from ..utilities.logging import Logger
from ..utilities.my_base_class import MyBaseClass
from ..utilities.config import UTIL_CONST
import uuid

class ConsumerGroup(MyBaseClass) :
    """
    Class for working with a group of consumers
    """

    @property
    def consumers(self) :
        return self.__consumers
    @property
    def topic_name(self) :
        return self.__topic_name

    def __init__(self,config_path,topic_name,*args,consumer_group_ID=str(uuid.uuid1()),n_consumers=UTIL_CONST.DEFAULT_N_THREADS,**other_kwargs) :
        """
        arguments:
        config_path = path to the config file that should be used to define the consumer group
        topic_name  = name of the topic to consume messages from

        keyword arguments:
        consumer_group_ID = ID to use for all consumers in the group (a new & unique ID is created by default)
        n_consumers = the number of Consumers to create in the group

        possible other keyword arguments: 
        logger = the logger object to use (a new one will be created if none is supplied)
        """
        self.__topic_name = topic_name
        self.__logger = other_kwargs.get('logger')
        if self.__logger is None :
            self.__logger = Logger(pathlib.Path(__file__).name.split('.')[0])
        #create a Consumer for each thread and subscribe it to the topic
        print(f'other_kwargs = {other_kwargs}')
        config_dict = MyDeserializingConsumer.get_config_dict(config_path,group_id=consumer_group_ID,**other_kwargs)
        self.__consumers = []
        for i in range(n_consumers) :
            consumer = MyDeserializingConsumer(config_dict,other_kwargs.get('logger'))
            self.__consumers.append(consumer)
        for consumer in self.__consumers :
            consumer.subscribe([self.__topic_name])
        super().__init__(*args,**other_kwargs)
