#imports
from .serialization import DataFileChunkSerializer, DataFileChunkDeserializer
from confluent_kafka.serialization import DoubleSerializer, IntegerSerializer, StringSerializer, DoubleDeserializer, IntegerDeserializer, StringDeserializer

def get_transformed_configs(configs,names_to_classes) :
    """
    Returns a configuration dictionary with some parameter names replaced by instances of classes

    configs = the configurations dictionary to alter and return
    names_to_classes = a dictionary whose keys are plaintext parameter values that may be in config files
                       and whose values are instances of the corresponding classes
    """
    for cfg_name,cfg_value in configs.items() :
        if cfg_value in names_to_classes.keys() :
            configs[cfg_name] = names_to_classes[cfg_value]()
    return configs

def get_replaced_configs(configs,replacement_type) :
    """
    Returns a configuration dictionary with (de)serialization parameters replaced by instances of corresponding classes

    configs = the configurations dictionary to alter and return
    replacement_type = a string indicating the type of replacement that should be performed
    """
    if replacement_type=='serialization' :
        names_classes = {
                'DoubleSerializer': DoubleSerializer,
                'IntegerSerializer': IntegerSerializer,
                'StringSerializer': StringSerializer,
                'DataFileChunkSerializer': DataFileChunkSerializer,
            }
    elif replacement_type=='deserialization' :
        names_classes = {
                'DoubleDeserializer': DoubleDeserializer,
                'IntegerDeserializer': IntegerDeserializer,
                'StringDeserializer': StringDeserializer,
                'DataFileChunkDeserializer': DataFileChunkDeserializer,
            }
    else :
        raise ValueError(f'ERROR: unrecognized replacement_type "{replacement_type}" in get_replaced_configs!')
    return get_transformed_configs(configs,names_classes)
