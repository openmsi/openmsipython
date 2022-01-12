#imports
from confluent_kafka import SerializingProducer
from kafkacrypto import KafkaProducer
from ..shared.logging import LogOwner
from .utilities import add_kwargs_to_configs
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

    @classmethod
    def from_file(cls,config_file_path,logger=None,**kwargs) :
        """
        config_file_path = path to the config file to use in defining this producer

        any keyword arguments will be added to the final producer configs (with underscores replaced with dots)
        """
        parser = MyKafkaConfigFileParser(config_file_path,logger=logger)
        #get the cluster and producer configurations
        all_configs = {**parser.cluster_configs,**parser.producer_configs}
        all_configs = add_kwargs_to_configs(all_configs,**kwargs)
        #if there are configs for KafkaCrypto, use a KafkaProducer
        if parser.kc_config_file_str is not None :
            if logger is not None :
                logger.debug(f'Produced messages will be encrypted using configs at {parser.kc_config_file_str}')
            kc = MyKafkaCrypto(parser.cluster_configs,parser.kc_config_file_str)
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
            #all_configs['debug']='broker,topic,msg'
            return cls(KafkaProducer,all_configs,kafkacrypto=kc,logger=logger)
        #otherwise use a SerializingProducer
        else :
            return cls(SerializingProducer,all_configs,logger=logger)

    def produce(self,*args,topic,key,value,**kwargs) :
        if isinstance(self.__producer,KafkaProducer) :
            key = self.__producer.ks(topic,key)
            value = self.__producer.vs(topic,value)
        self.__producer.produce(*args,topic=topic,key=key,value=value,**kwargs)
    def poll(self,*args,**kwargs) :
        self.__producer.poll(*args,**kwargs)
    def flush(self,*args,**kwargs) :
        self.__producer.flush(*args,**kwargs)