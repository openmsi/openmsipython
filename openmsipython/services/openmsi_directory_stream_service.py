#imports
from openmsipython.command_line_scripts.upload_data_files_added_to_directory import main
from openmsipython.utilities.config_file_parser import ConfigFileParser
from openmsipython.utilities.argument_parsing import existing_dir, config_path, int_power_of_two
from openmsipython.data_file_io.config import RUN_OPT_CONST
from argparse import Namespace
import sys, pathlib

#helper function to get the configs from the file and make sure they are all valid, and then return them in a namespace
#basically cloning the command line argument parser from the command line script, but using the arguments from the config file
def get_args(config_file_path) :
    #parse the config file
    cfp = ConfigFileParser(pathlib.Path(config_file_path))
    configs = cfp.get_config_dict_for_groups('openmsi_directory_stream_service')
    #if the cluster and producer configs are also specified in the given file, add it as the "config" argument to the command line script
    if 'cluster' in cfp.available_group_names and 'producer' in cfp.available_group_names :
        #but in this case the 'cluster_producer_config' argument would be ambiguous
        if 'cluster_producer_config' in configs.keys() :
            msg = 'ERROR: ambiguous cluster/producer configuration. Specify cluster/producer configs EITHER '
            msg+=f'in the {config_file_path} file or in the file at "cluster_producer_config", but not both.'
            raise ValueError(msg)
        configs['config']=config_file_path
    #otherwise, check if a different config file to use for the cluster/producer configs was given
    if 'cluster_producer_config' in configs.keys() :
        configs['config'] = config_path(configs['cluster_producer_config']) 
    #check the other arguments to make sure they're the correct type and replace any that weren't given with the defaults
    arg_checks = {'file_directory':{'type':existing_dir,'default':None},
                  'config':{'type':config_path,'default':config_path(RUN_OPT_CONST.DEFAULT_CONFIG_FILE)},
                  'topic_name':{'type':str,'default':RUN_OPT_CONST.DEFAULT_TOPIC_NAME}, 
                  'n_threads':{'type':int,'default':RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS},      
                  'chunk_size':{'type':int_power_of_two,'default':RUN_OPT_CONST.DEFAULT_CHUNK_SIZE},
                  'queue_max_size':{'type':int,'default':RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE},
                  'new_files_only':{'type':bool,'default':True},
                 }
    for argname,argdict in arg_checks.items() :
        #if the argument was given
        if argname in configs.keys() :
            #make sure it's of the right type
            try :
                configs[argname] = argdict['type'](configs[argname])
            except Exception as e :
                raise (e)
        else :
            #if there's no default, throw an error
            if argdict['default'] is None :
                raise RuntimeError(f'ERROR: missing argument {argname} in!')
            configs[argname] = argdict['default']
    #return a Namespace with all of the necessary arguments
    args = Namespace(file_directory=configs['file_directory'],
                     config=configs['config'],
                     topic_name=configs['topic_name'],
                     n_threads=configs['n_threads'],
                     chunk_size=configs['chunk_size'],
                     queue_max_size=configs['queue_max_size'],
                     update_seconds=configs['update_seconds'],
                     new_files_only=configs['new_files_only'],
                    )
    return args

#call the main method of the command line script
if __name__=='__main__' :
    if len(sys.argv)!=2 :
        raise RuntimeError('ERROR: must provide exactly one argument (the path to the config file)!')
    main(args=get_args(sys.argv[1]))
