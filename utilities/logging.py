#imports
import logging

class Logger :
    """
    Class for a general logger. Logs messages and raises exceptions
    """

    def __init__(self) :
        self._logger_obj = logging.getLogger("general")
        self._logger_obj.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s  [%(funcName)s]","%Y-%m-%d %H:%M:%S"))
        self._logger_obj.addHandler(handler)

    #functions for logging different levels of messages
    
    def info(self,msg) :
        self._logger_obj.info(msg)
    
    def warning(self,msg) :
        self._logger_obj.warning(msg)

    #function to log an error message and optionally raise an exception with the same message

    def error(self,msg,exception_type=None) :
        self._logger_obj.error(msg)
        if exception_type is not None :
            raise exception_type(msg)

