#imports
import pathlib, math, uuid
from argparse import ArgumentParser
from ..data_file_io.config import RUN_OPT_CONST
from .config import UTIL_CONST

#################### MISC. FUNCTIONS ####################

#convert a string or path argument into a path to a file, checking if it exists
def existing_file(argstring) :
    if pathlib.Path.is_file(pathlib.Path(argstring)) :
        return pathlib.Path(argstring).resolve()
    raise FileNotFoundError(f'ERROR: file {argstring} does not exist!')

#convert a string or path argument into a directory path, checking if it exists
def existing_dir(argstring) :
    if pathlib.Path.is_dir(pathlib.Path(argstring)) :
        return pathlib.Path(argstring).resolve()
    raise FileNotFoundError(f'ERROR: directory {argstring} does not exist!')

#convert a string or path argument into a directory path, creating it if necessary
def create_dir(argstring) :
    if argstring is None : #Then the argument wasn't given and nothing should be done
        return None
    if pathlib.Path.is_dir(pathlib.Path(argstring)) :
        return pathlib.Path(argstring).resolve()
    try :
        pathlib.Path.mkdir(pathlib.Path(argstring),exist_ok=True)
        return pathlib.Path(argstring).resolve()
    except Exception as e :
        raise RuntimeError(f'ERROR: failed to create directory with name {argstring}! error: {e}')

#convert a string or path argument into a config file path (raise an exception if the file can't be found)
def config_path(configarg) :
    if isinstance(configarg,str) and '.' not in configarg :
        configarg+=UTIL_CONST.CONFIG_FILE_EXT
    if pathlib.Path.is_file(pathlib.Path(configarg)) :
        return pathlib.Path(configarg).resolve()
    if pathlib.Path.is_file(UTIL_CONST.CONFIG_FILE_DIR / configarg) :
        return (UTIL_CONST.CONFIG_FILE_DIR / configarg).resolve()
    raise ValueError(f'ERROR: config argument {configarg} is not a recognized config file!')

#make sure a given value is a nonzero integer power of two (or can be converted to one)
def int_power_of_two(argval) :
    if not isinstance(argval,int) :
        try :
            argval=int(argval)
        except Exception as e :
            raise ValueError(f'ERROR: could not convert {argval} to an integer in int_power_of_two! Exception: {e}')
    if argval<=0 or math.ceil(math.log2(argval))!=math.floor(math.log2(argval)) :
        raise ValueError(f'ERROR: invalid argument: {argval} must be a (nonzero) power of two!')
    return argval

#make sure a given value is a positive integer
def positive_int(argval) :
    try :
        argval = int(argval)
    except Exception as e :
        raise ValueError(f'ERROR: could not convert {argval} to an integer in positive_int! Exception: {e}')
    if (not isinstance(argval,int)) or (argval<1) :
        raise ValueError(f'ERROR: invalid argument: {argval} must be a positive integer!')
    return argval

#################### MYARGUMENTPARSER CLASS ####################

class MyArgumentParser(ArgumentParser) :
    """
    Class to make it easier to get an ArgumentParser with some commonly-used arguments in it
    """

    ARGUMENTS = {
        'filepath':{'positional':True,
                    'kwargs':{'type':existing_file,'help':'Path to the data file to use'}},
        'output_dir':{'positional':True,
                      'kwargs':{'type':create_dir,'help':'Path to the directory to put output in'}},
        'upload_dir':{'positional':True,
                      'kwargs':{'type':existing_dir,'help':'Path to the directory to watch for files to upload'}},
        'config':{'positional':False,
                  'kwargs':{'default':RUN_OPT_CONST.DEFAULT_CONFIG_FILE,'type':config_path,
                            'help':f'Name of config file to use in {UTIL_CONST.CONFIG_FILE_DIR.resolve()}, or path to a file in a different location'}},
        'topic_name':{'positional':False,
                      'kwargs':{'default':RUN_OPT_CONST.DEFAULT_TOPIC_NAME,'help':'Name of the topic to produce to or consume from'}},
        'n_threads':{'positional':False,
                     'kwargs':{'default':UTIL_CONST.DEFAULT_N_THREADS,'type':positive_int,'help':'Maximum number of threads to use'}},
        'chunk_size':{'positional':False,
                      'kwargs':{'default':RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,'type':int_power_of_two,
                                'help':'Max size (in bytes) of chunks into which files should be broken as they are uploaded'}},
        'queue_max_size':{'positional':False,
                          'kwargs':{'default':RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE,'type':int,
                                    'help':"""Maximum number of items to allow in the upload queue at a time. 
                                              Use to limit RAM usage or throttle production rate if necessary."""}},
        'update_seconds':{'positional':False,
                          'kwargs':{'default':UTIL_CONST.DEFAULT_UPDATE_SECONDS,'type':int,
                                    'help':'Number of seconds between printing a "." to the console to indicate the program is alive'}},
        'new_files_only':{'positional':False,
                          'kwargs':{'action':'store_true',
                                    'help':"""Add this flag to only upload files added to the directory after this code is already running
                                              (by default files already existing in the directory at startup will be uploaded as well)"""}},
        'consumer_group_ID':{'positional':False,
                             'kwargs':{'default':str(uuid.uuid1()),
                                       'help':'ID to use for all consumers in the group (by default a new, unique, ID will be created)'}},
        'pdv_plot_type':{'positional':False,
                         'kwargs':{'choices':['spall','velocity'],'default':'spall',
                                   'help':'Type of analysis to perform ("spall" or "velocity")'}},
        'optional_output_dir':{'positional':False,
                               'kwargs':{'type':create_dir,
                                         'help':'Path to directory to put output in'}},
    }

    def __init__(self,*argnames,**kwargs) :
        if len(argnames)<1 :
            raise ValueError('ERROR: must give at least one argument name to create an argument parser!')
        super().__init__(**kwargs)
        parsed_argnames = []
        for argname in argnames :
            if argname in self.ARGUMENTS.keys() :
                if self.ARGUMENTS[argname]['positional'] :
                    argname_to_add = argname 
                else :
                    if argname.startswith('optional_') :
                        argname_to_add = f'--{argname[len("optional_"):]}'
                    else :
                        argname_to_add = f'--{argname}'
                if 'default' in self.ARGUMENTS[argname]['kwargs'].keys() :
                    if 'help' in self.ARGUMENTS[argname]['kwargs'].keys() :
                        self.ARGUMENTS[argname]['kwargs']['help']+=f" (default = {self.ARGUMENTS[argname]['kwargs']['default']})"
                    else :
                        self.ARGUMENTS[argname]['kwargs']['help']=f"default = {self.ARGUMENTS[argname]['kwargs']['default']}"
                self.add_argument(argname_to_add,**self.ARGUMENTS[argname]['kwargs'])
                parsed_argnames.append(argname)
        if tuple(parsed_argnames)!=argnames :
            errmsg = f'ERROR: some requested arguments could not be identified ({[a for a in argnames if a not in parsed_argnames]}'
            errmsg+=' not parsed)'
            raise ValueError(errmsg)
