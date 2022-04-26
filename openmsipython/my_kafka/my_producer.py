#imports
import time
from confluent_kafka import SerializingProducer
from kafkacrypto import KafkaProducer
from ..shared.logging import LogOwner
from ..shared.producible import Producible
from .utilities import add_kwargs_to_configs, producer_callback, PRODUCER_CALLBACK_LOGGER
from .config_file_parser import MyKafkaConfigFileParser
from .my_kafka_crypto import MyKafkaCrypto
from .serialization import CompoundSerializer

class MyProducer(LogOwner) :
    """
    Convenience class for working with a Producer of some type
    """

    def __init__(self,producer_type,configs,kafkacrypto=None,**kwargs) :
        """
        producer_type = the type of Producer underlying this object
        configs = a dictionary of configurations to pass to the producer to create it
        """
        super().__init__(**kwargs)
        if producer_type==KafkaProducer :
            if kafkacrypto is None :
                self.logger.error('ERROR: creating a KafkaProducer requires holding onto its KafkaCrypto objects!')
            self.__kafkacrypto = kafkacrypto
            self.__producer = producer_type(**configs)
        elif producer_type==SerializingProducer :
            self.__producer = producer_type(configs)
        else :
            self.logger.error(f'ERROR: Unrecognized producer type {producer_type} for MyProducer!',ValueError)
        # set the interval at which to call poll() to 100 * linger.ms
        self.__poll_interval = 100*0.005 
        if 'linger.ms' in configs.keys() :
            self.__poll_interval = 100*0.001*float(configs['linger.ms'])
        self.__last_poll_time = time.perf_counter()

    @classmethod
    def from_file(cls,config_file_path,logger=None,**kwargs) :
        """
        config_file_path = path to the config file to use in defining this producer

        any keyword arguments will be added to the final producer configs (with underscores replaced with dots)
        """
        parser = MyKafkaConfigFileParser(config_file_path,logger=logger)
        #get the broker and producer configurations
        all_configs = {**parser.broker_configs,**parser.producer_configs}
        all_configs = add_kwargs_to_configs(all_configs,**kwargs)
        #all_configs['debug']='broker,topic,msg'
        #if there are configs for KafkaCrypto, use a KafkaProducer
        if parser.kc_config_file_str is not None :
            if logger is not None :
                logger.debug(f'Produced messages will be encrypted using configs at {parser.kc_config_file_str}')
            kc = MyKafkaCrypto(parser.broker_configs,parser.kc_config_file_str)
            if 'key.serializer' in all_configs.keys() :
                keyser = CompoundSerializer(all_configs.pop('key.serializer'),kc.key_serializer)
            else :
                keyser = kc.key_serializer
            if 'value.serializer' in all_configs.keys() :
                valser = CompoundSerializer(all_configs.pop('value.serializer'),kc.value_serializer)
            else :
                valser = kc.value_serializer
            all_configs['key_serializer']=keyser
            all_configs['value_serializer']=valser
            return cls(KafkaProducer,all_configs,kafkacrypto=kc,logger=logger)
        #otherwise use a SerializingProducer
        else :
            return cls(SerializingProducer,all_configs,logger=logger)

    def produce_from_queue(self,queue,topic_name,print_every=1000,timeout=60,retry_sleep=5) :
        """
        Get Producible objects from a given queue and Produce them to the given topic.
        Runs until "None" is pulled from the Queue
        Meant to be run in multiple threads in parallel

        queue       = the Queue holding objects that should be Produced
        topic_name  = the name of the topic to Produce to
        print_every = how often to print/log progress messages
        timeout     = max time (s) to wait for the message to be produced in the event of (repeated) BufferError(s)
        retry_sleep = how long (s) to wait between produce attempts if one fails with a BufferError
        """
        #set the logger so the callback can use it
        PRODUCER_CALLBACK_LOGGER.logger = self.logger
        #get the next object from the Queue
        obj = queue.get()
        #loop until "None" is pulled from the Queue
        while obj is not None :
            if isinstance(obj,Producible) :
                #log a line about this message if applicable
                logmsg = obj.get_log_msg(print_every)
                if logmsg is not None :
                    self.logger.info(logmsg)
                #produce the message to the topic
                success=False; total_wait_secs=0 
                if (not success) and total_wait_secs<timeout :
                    try :
                        self.produce(topic=topic_name,key=obj.msg_key,value=obj.msg_value,on_delivery=producer_callback)
                        success=True
                    except BufferError :
                        time.sleep(retry_sleep)
                        total_wait_secs+=retry_sleep
                if not success :
                    warnmsg = f'WARNING: message with key {obj.msg_key} failed to buffer for more than '
                    warnmsg+= f'{total_wait_secs}s and was dropped!'
                    self.logger.warning(warnmsg)
                if (time.perf_counter()-self.__last_poll_time)>self.__poll_interval :
                    self.poll(self.__poll_interval/100.)
                    self.__last_poll_time = time.perf_counter()
            else :
                warnmsg = f'WARNING: found an object of type {type(obj)} in a Producer queue that should only contain '
                warnmsg+= 'Producible objects. This object will be skipped!'
                self.logger.warning(warnmsg)
            #get the next object in the Queue
            obj = queue.get()
        queue.task_done()

    def produce(self,*args,topic,key,value,**kwargs) :
        if isinstance(self.__producer,KafkaProducer) :
            key = self.__producer.ks(topic,key)
            value = self.__producer.vs(topic,value)
        self.__producer.produce(*args,topic=topic,key=key,value=value,**kwargs)
    
    def poll(self,*args,**kwargs) :
        self.__producer.poll(*args,**kwargs)
    
    def flush(self,*args,**kwargs) :
        self.__producer.flush(*args,**kwargs)

    def close(self) :
        try :
            if self.__kafkacrypto :
                self.__kafkacrypto.close()
        except :
            pass
        finally :
            self.__kafkacrypto = None
