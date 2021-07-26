#imports
import uuid
from ..utilities.config import UTIL_CONST
from .my_consumers import MyDeserializingConsumer

class ConsumerGroup :
    """
    Class for working with a group of consumers
    """
    _consumer_type = MyDeserializingConsumer

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
        """
        self.__topic_name = topic_name
        #create a Consumer for each thread and subscribe it to the topic
        config_dict = self._consumer_type.get_config_dict(config_path,group_id=consumer_group_ID,**other_kwargs)
        self.__consumers = []
        for i in range(n_consumers) :
            consumer = MyDeserializingConsumer(config_dict)
            self.__consumers.append(consumer)
        for consumer in self.__consumers :
            consumer.subscribe([self.__topic_name])        
