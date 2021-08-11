#imports
from .serialization import DataFileChunkSerializer, DataFileChunkDeserializer
from confluent_kafka.serialization import DoubleSerializer, IntegerSerializer, StringSerializer
from confluent_kafka.serialization import DoubleDeserializer, IntegerDeserializer, StringDeserializer

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

def get_next_message(consumer,logger,*poll_args,**poll_kwargs) :
    """
    Call "poll" for the given consumer and return any successfully consumed message
    otherwise log a warning if there's an error
    """
    consumed_msg = None
    try :
        consumed_msg = consumer.poll(*poll_args,**poll_kwargs)
    except Exception as e :
        warnmsg = 'WARNING: encountered an error in a call to consumer.poll() and will skip the offending message. '
        warnmsg+= f'Error: {e}'
        logger.warning(warnmsg)
        return
    if consumed_msg is not None :
        if consumed_msg.error() is not None or consumed_msg.value() is None :
            warnmsg = f'WARNING: unexpected consumed message, consumed_msg = {consumed_msg}'
            warnmsg+= f', consumed_msg.error() = {consumed_msg.error()}, consumed_msg.value() = {consumed_msg.value()}'
            logger.warning(warnmsg)
        return consumed_msg.value()
    else :
        return
