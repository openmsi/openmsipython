#several helper functions used as ArgumentParser callbacks

#imports
import pathlib, math

#################### FILE-SCOPE CONSTANTS ####################

CONFIG_FILE_EXT = '.config'
CONFIG_FILE_DIR = pathlib.Path(__file__).parent.parent / 'my_kafka' / 'config_files'

#################### MISC. FUNCTIONS ####################

#helper function to convert a string argument into a path to a file, checking if it exists
def existing_file(argstring) :
    if pathlib.Path.is_file(pathlib.Path(argstring)) :
        return pathlib.Path(argstring).resolve().absolute()
    raise ValueError(f'ERROR: file {argstring} does not exist!')

#helper function to convert a string argument into a directory path, checking if it exists
def existing_dir(argstring) :
    if pathlib.Path.is_dir(pathlib.Path(argstring)) :
        return pathlib.Path(argstring).resolve().absolute()
    raise ValueError(f'ERROR: directory {argstring} does not exist!')

#helper function to convert a string argument into a directory path, creating it if necessary
def create_dir(argstring) :
    if pathlib.Path.is_dir(pathlib.Path(argstring)) :
        return pathlib.Path(argstring).resolve().absolute()
    try :
        pathlib.Path.mkdir(argstring,exist_ok=True)
        return pathlib.Path(argstring).resolve().absolute()
    except Exception as e :
        raise RuntimeError(f'ERROR: failed to create directory with name {argstring}! error: {e}')

#helper function to convert a string argument into a path (raise an exception if the file can't be found)
def config_path(configarg) :
    if '.' not in configarg :
        configarg+=CONFIG_FILE_EXT
    if pathlib.Path.is_file(pathlib.Path(configarg)) :
        return pathlib.Path(configarg).resolve().absolute()
    if pathlib.Path.is_file(CONFIG_FILE_DIR / configarg) :
        return (CONFIG_FILE_DIR / configarg).resolve().absolute()
    raise ValueError(f'ERROR: config argument {configarg} is not a recognized file!')

#helper function to make sure a given value is a nonzero integer power of two
def int_power_of_two(argval) :
    if argval<=0 or math.ceil(math.log2(argval))!=math.floor(math.log2(argval)) :
        raise ValueError(f'ERROR: invalid argument: {argval} must be a (nonzero) power of two!')
    return argval