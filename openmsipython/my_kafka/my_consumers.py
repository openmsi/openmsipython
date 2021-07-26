#imports
from .utilities import get_replaced_configs, get_next_message
from ..utilities.config_file_parser import ConfigFileParser
from confluent_kafka import Consumer, DeserializingConsumer
import uuid

class MyConsumer(Consumer) :
    """
    Class to extend Kafka Consumers for specific scenarios
    """

    def __init__(self,config_dict) :
        """
        config_dict = dictionary of configuration parameters to set up the Consumer
        """
        super().__init__(config_dict)

    @classmethod
    def from_file(cls,config_file_path,**kwargs) :
        """
        config_file_path = path to the config file to use in defining this consumer

        !!!!! any keyword arguments (that aren't 'logger') will be added to the configuration (with underscores replaced with dots) !!!!!
        """
        parser = ConfigFileParser(config_file_path,logger=kwargs.get('logger'))
        configs = parser.get_config_dict_for_groups(['cluster','consumer'])
        for argname,arg in kwargs.items() :
            if argname=='logger' :
                continue
            configs[argname.replace('_','.')]=arg
        #if the group.id has been set as "new" generate a new group ID
        if 'group.id' in configs.keys() and configs['group.id'].lower()=='create_new' :
            configs['group.id']=str(uuid.uuid1())
        #if the auto.offset.reset was given as "none" then remove it from the configs
        if 'auto.offset.reset' in configs.keys() and configs['auto.offset.reset']=='none' :
            del configs['auto.offset.reset']
        return cls(configs)
    
    def get_next_message(self,logger,*poll_args,**poll_kwargs) :
        return get_next_message(self,logger,*poll_args,**poll_kwargs)

class MyDeserializingConsumer(DeserializingConsumer) :
    """
    Class to extend Kafka Consumers for specific scenarios
    """

    def __init__(self,config_dict) :
        """
        config_dict = dictionary of configuration parameters to set up the DeserializingConsumer
        """
        super().__init__(config_dict)

    @classmethod
    def from_file(cls,config_file_path,**kwargs) :
        """
        config_file_path = path to the config file to use in defining this consumer

        !!!!! any keyword arguments (that aren't 'logger') will be added to the configuration (with underscores replaced with dots) !!!!!
        """
        return cls(cls.get_config_dict(config_file_path,**kwargs))

    @staticmethod
    def get_config_dict(config_file_path,**kwargs) :
        """
        Return the configuration dictionary to use based on a given config file and including any replacements in the keyword arguments
        """
        parser = ConfigFileParser(config_file_path,logger=kwargs.get('logger'))
        configs = parser.get_config_dict_for_groups(['cluster','consumer'])
        for argname,arg in kwargs.items() :
            if argname=='logger' :
                continue
            configs[argname.replace('_','.')]=arg
        #if the group.id has been set as "new" generate a new group ID
        if 'group.id' in configs.keys() and configs['group.id'].lower()=='create_new' :
            configs['group.id']=str(uuid.uuid1())
        #if the auto.offset.reset was given as "none" then remove it from the configs
        if 'auto.offset.reset' in configs.keys() and configs['auto.offset.reset']=='none' :
            del configs['auto.offset.reset']
        #if one of several recognized deserializers have been given as config paramenters for the key/value deserializer, replace them with the actual class
        configs = get_replaced_configs(configs,'deserialization')
        return configs

    def get_next_message(self,logger,*poll_args,**poll_kwargs) :
        return get_next_message(self,logger,*poll_args,**poll_kwargs) 
