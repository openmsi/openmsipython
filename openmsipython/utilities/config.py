# Constants for routines in utilities

class UtilityConstants :
    @property
    def DEFAULT_N_THREADS(self) :
        return 3      # default number of threads to use in general
    @property
    def DEFAULT_UPDATE_SECONDS(self) :
        return 30     # how many seconds to wait by default between printing the "still alive" character/message for a running process


UTIL_CONST = UtilityConstants()
