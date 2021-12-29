#imports
from confluent_kafka import Producer, SerializingProducer
from kafkacrypto import KafkaProducer
from ..shared.config_file_parser import ConfigFileParser
from .utilities import get_replaced_configs, find_kc_config_file_from_parser
from .serialization import CompoundSerializer
from .my_kafka_crypto import MyKafkaCrypto

class MyProducer(Producer) :
    """
    Class to extend Kafka Producers for specific scenarios
    """

    def __init__(self,config_dict) :
        super().__init__(config_dict)

    @classmethod
    def from_file(cls,config_file_path,**kwargs) :
        """
        config_file_path = path to the config file to use in defining this producer

        !!!!! any keyword arguments (that aren't 'logger') will be added to the configuration !!!!!
        (with underscores replaced with dots)
        """
        parser = ConfigFileParser(config_file_path,logger=kwargs.get('logger'))
        configs = parser.get_config_dict_for_groups(['cluster','producer'])
        for argname,arg in kwargs.items() :
            if argname=='logger' :
                continue
            configs[argname.replace('_','.')]=arg
        return cls(configs)

class MySerializingProducer(SerializingProducer) :
    """
    Class to extend Kafka SerializingProducers for specific scenarios
    """

    def __init__(self,config_dict) :
        super().__init__(config_dict)

    @classmethod
    def from_file(cls,config_file_path,**kwargs) :
        """
        config_file_path = path to the config file to use in defining this producer

        !!!!! any keyword arguments (that aren't 'logger') will be added to the configuration !!!!!
        (with underscores replaced with dots)
        """
        logger = kwargs.get('logger')
        parser = ConfigFileParser(config_file_path,logger=logger)
        #get the cluster and producer configurations
        cluster_configs = parser.get_config_dict_for_groups('cluster')
        producer_configs = parser.get_config_dict_for_groups('producer')
        all_configs = {**cluster_configs,**producer_configs}
        for argname,arg in kwargs.items() :
            if argname=='logger' :
                continue
            all_configs[argname.replace('_','.')]=arg
        #if one of several recognized serializers have been given as config paramenters for the key/value serializer, 
        #replace them with the actual class
        all_configs = get_replaced_configs(all_configs,'serialization')
        #look for special configs for kafkacrypto
        kc_config_file = find_kc_config_file_from_parser(parser,logger=logger)
        if kc_config_file is not None :
            if logger is not None :
                logger.debug(f'Produced messages will be encrypted using configs at {kc_config_file}')
            kc = MyKafkaCrypto(cluster_configs,kc_config_file)
            if 'key.serializer' in all_configs.keys() :
                keyser = CompoundSerializer(all_configs.pop('key.serializer'),kc.key_serializer)
            else :
                keyser = kc.key_serializer
            if 'value.serializer' in all_configs.keys() :
                valser = CompoundSerializer(all_configs.pop('value.serializer'),kc.value_serializer)
            else :
                valser = kc.value_serializer
            #all_configs['debug']='broker,topic,msg'
            return KafkaProducer(**all_configs,key_serializer=keyser,value_serializer=valser)
        else :
            return cls(all_configs)
