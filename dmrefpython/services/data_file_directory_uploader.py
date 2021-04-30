#imports
from dmrefpython.command_line_scripts.upload_data_files_added_to_directory import main
from dmrefpython.utilities.config_file_parser import ConfigFileParser
from dmrefpython.utilities.argument_parsing import existing_dir, config_path, int_power_of_two
from argparse import Namespace
import sys, pathlib

#helper function to get the configs from the file and make sure they are all valid, and then return them in a namespace
#basically cloning the command line argument parser from the command line script, but using the arguments from the config file
def get_args(config_file_path) :
    #parse the config file
    cfp = ConfigFileParser(pathlib.Path(config_file_path))
    configs = cfp.get_config_dict_for_groups('data_file_directory_uploader')
    #add the config file path as an argument called "config"
    configs['config']=config_path(config_file_path)
    #check the other arguments to make sure they're the correct type and replace them in the dictionary
    arg_checks = {'file_directory':existing_dir,
                  'topic_name':str, 
                  'n_threads':int,      
                  'chunk_size':int_power_of_two,
                  'queue_max_size':int,
                  'update_seconds':int,
                  'new_files_only':bool,
                 }
    for argname,argfunc in arg_checks.items() :
        if argname not in configs.keys() :
            raise RuntimeError(f'ERROR: missing argument {argname} in!')
        try :
            configs[argname] = argfunc(configs[argname])
        except Exception as e :
            raise (e)
    #return a Namespace with the populated arguments
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

#call the main method of the command line script (first argument to this script is the path to the config file to use)
main(args=get_args(sys.argv[1]),safe_quit_on_exit=True)
