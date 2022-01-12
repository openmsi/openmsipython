#imports
import time
from confluent_kafka import DeserializingConsumer
from kafkacrypto import KafkaConsumer
from ..shared.logging import LogOwner
from .utilities import add_kwargs_to_configs
from .config_file_parser import MyKafkaConfigFileParser
from .my_kafka_crypto import MyKafkaCrypto
from .serialization import CompoundDeserializer

class MyConsumer(LogOwner) :
    """
    Convenience class for working with a Consumer of some type
    """

    MAX_WAIT_TIME_PER_KC_MESSAGE = 10 #in seconds

    def __init__(self,consumer_type,configs,kafkacrypto=None,**kwargs) :
        """
        consumer_type = the type of Consumer underlying this object
        configs = a dictionary of configurations to pass to the consumer to create it
        """
        super().__init__(**kwargs)
        if consumer_type==KafkaConsumer :
            if kafkacrypto is None :
                self.logger.error('ERROR: creating a KafkaConsumer requires holding onto its KafkaCrypto objects!')
            self.__kafkacrypto = kafkacrypto
            self.__consumer = consumer_type(**configs)
        elif consumer_type==DeserializingConsumer :
            self.__consumer = consumer_type(configs)
        else :
            self.logger.error(f'ERROR: Unrecognized consumer type {consumer_type} for MyConsumer!',ValueError)

    @staticmethod
    def get_consumer_args_kwargs(config_file_path,logger=None,**kwargs) :
        """
        Return the arguments and keyword arguments that should be used to create a MyConsumer based on the configs

        config_file_path = path to the config file to use in defining this consumer

        any keyword arguments will be added to the final consumer configs (with underscores replaced with dots)

        Used to quickly instantiate more than one identical MyConsumer for a ConsumerGroup
        """
        parser = MyKafkaConfigFileParser(config_file_path,logger=logger)
        ret_kwargs = {}
        #get the cluster and consumer configurations
        all_configs = {**parser.cluster_configs,**parser.consumer_configs}
        all_configs = add_kwargs_to_configs(all_configs,**kwargs)
        #if there are configs for KafkaCrypto, use a KafkaConsumer
        if parser.kc_config_file_str is not None :
            if logger is not None :
                logger.debug(f'Consumed messages will be decrypted using configs at {parser.kc_config_file_str}')
            kc = MyKafkaCrypto(parser.cluster_configs,parser.kc_config_file_str)
            if 'key.deserializer' in all_configs.keys() :
                keydes = CompoundDeserializer(kc.key_deserializer,all_configs.pop('key.deserializer'))
            else :
                keydes = kc.key_deserializer
            if 'value.deserializer' in all_configs.keys() :
                valdes = CompoundDeserializer(kc.value_deserializer,all_configs.pop('value.deserializer'))
            else :
                valdes = kc.value_deserializer
            all_configs['key_deserializer']=keydes
            all_configs['value_deserializer']=valdes
            #all_configs['debug']='broker,topic,msg'
            ret_args = [KafkaConsumer,all_configs]
            ret_kwargs['kafkacrypto']=kc
        #otherwise use a DeserializingConsumer
        else :
            ret_args = [DeserializingConsumer,all_configs]
        ret_kwargs['logger'] = logger
        return ret_args, ret_kwargs

    @classmethod
    def from_file(cls,*args,**kwargs) :
        args_to_use, kwargs_to_use = MyConsumer.get_consumer_args_kwargs(*args,**kwargs)
        return cls(*args_to_use,**kwargs_to_use)

    def get_next_message_value(self,*poll_args,**poll_kwargs) :
        """
        Call "poll" for this consumer and return any successfully consumed message's value
        otherwise log a warning if there's an error
        """
        consumed_msg = None
        try :
            #import logging
            #logging.basicConfig(level=logging.DEBUG)
            #logging.getLogger('kafkaCrypto').setLevel(level=logging.DEBUG)
            #print(f'Calling poll on consumer {self.__consumer}')
            consumed_msg = self.__consumer.poll(*poll_args,**poll_kwargs)
            #print(f'Returned from poll for consumer {self.__consumer}')
        except Exception as e :
            warnmsg = 'WARNING: encountered an error in a call to consumer.poll() and this message will be skipped. '
            warnmsg+= f'Exception: {e}'
            self.logger.warning(warnmsg)
            #raise e
            return
        if consumed_msg is not None and consumed_msg!={} :
            #wait for the message to be decrypted if necessary
            if isinstance(self.__consumer,KafkaConsumer) :
                elapsed = 0
                while (not consumed_msg.value.isCleartext()) and elapsed<MyConsumer.MAX_WAIT_TIME_PER_KC_MESSAGE :
                    time.sleep(1)
                    elapsed+=1
                if consumed_msg.value.isCleartext() :
                    return consumed_msg.value
                else :
                    self.logger.warning('WARNING: failed to decrypt a message!')
            else :
                if consumed_msg.error() is not None or consumed_msg.value() is None :
                    warnmsg = f'WARNING: unexpected consumed message, consumed_msg = {consumed_msg}'
                    warnmsg+= f', consumed_msg.error() = {consumed_msg.error()}, consumed_msg.value() = {consumed_msg.value()}'
                    self.logger.warning(warnmsg)
                return consumed_msg.value()
        else :
            return

    def subscribe(self,*args,**kwargs) :
        self.__consumer.subscribe(*args,**kwargs)
    def close(self,*args,**kwargs) :
        self.__consumer.close(*args,**kwargs)
