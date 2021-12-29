#imports
import pathlib
from confluent_kafka.serialization import DoubleSerializer, IntegerSerializer, StringSerializer
from confluent_kafka.serialization import DoubleDeserializer, IntegerDeserializer, StringDeserializer
from ..shared.config import UTIL_CONST
from .serialization import DataFileChunkSerializer, DataFileChunkDeserializer

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

def find_kc_config_file_from_parser(parser,logger=None) :
    """
    Returns the path to the config file that KafkaCrypto needs given a parser for a general config file.
    Return value is a string as expected by KafkaCrypto.
    If no config file is found according to the conventions listed below, this function returns None 
    and it will be assumed that no configuration for KafkaCrypto exists

    Options are:
    1) The regular config file also has the KafkaCrypto configs in it, as indicated by the presence of 
       the "node_id" in the DEFAULT section
    2) The regular config file has a "kafkacrypto" section with a "config_file" parameter that is the 
       path to the KafkaCrypo config file
    3) The regular config file has a "kafkacrypto" section with a "node_id" parameter corresponding to 
       a named subdirectory in openmsipython/my_kafka/config_files that was created when the node was provisioned
    """
    #option 1 above
    if parser.has_default and 'node_id' in (parser.get_config_dict_for_groups('DEFAULT')).keys() :
        return str(parser.filepath)
    elif 'kafkacrypto' in parser.available_group_names :
        kc_configs = parser.get_config_dict_for_groups('kafkacrypto')
        #option 2 above
        if 'config_file' in kc_configs.keys() :
            path_as_str = (kc_configs['config_file']).lstrip('file#')
            if not pathlib.Path(path_as_str.is_file()) :
                errmsg = f'ERROR: KafkaCrypto config file {path_as_str} (from config file {parser.filepath}) not found!'
                if logger is not None :
                    logger.error(errmsg,FileNotFoundError)
                else :
                    raise FileNotFoundError(errmsg)
            return path_as_str
        #option 3 above
        elif 'node_id' in kc_configs.keys() :
            node_id = kc_configs['node_id']
            dirpath = UTIL_CONST.CONFIG_FILE_DIR / node_id
            filepath = dirpath / f'{node_id}.config'
            if (not dirpath.is_dir()) or (not filepath.is_file()) :
                errmsg = f'ERROR: no KafkaCrypto config file found in the default location ({filepath}) '
                errmsg+= f'for node ID = {node_id}'
                if logger is not None :
                    logger.error(errmsg,FileNotFoundError)
                else :
                    raise FileNotFoundError(errmsg)
            return str(filepath)
    #no config file found
    return None

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
