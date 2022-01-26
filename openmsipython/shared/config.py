#imports
import pathlib

class UtilityConstants :
    """
    Constants for routines in utilities
    """
    @property
    def CONFIG_FILE_EXT(self) :
        return '.config' # default extension for config files
    @property
    def CONFIG_FILE_DIR(self) :
        return pathlib.Path(__file__).parent.parent / 'my_kafka' / 'config_files'
    @property
    def DEFAULT_N_THREADS(self) :
        return 2      # default number of threads to use in general
    @property
    def DEFAULT_UPDATE_SECONDS(self) :
        return 30     # how many seconds to wait by default between printing the "still alive" character/message 
                      #for a running process

UTIL_CONST = UtilityConstants()
