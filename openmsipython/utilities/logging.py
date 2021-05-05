#imports
import logging, pathlib

class Logger :
    """
    Class for a general logger. Logs messages and raises exceptions
    """

    @property
    def formatter(self):
        return logging.Formatter('[%(name)s at %(asctime)s] %(message)s','%Y-%m-%d %H:%M:%S')

    def __init__(self,name=None,level=logging.DEBUG,filepath=None,filelevel=logging.INFO) :
        """
        name = the name for this logger to use (probably something like the top module that owns it)
        """
        self._name = name
        if self._name is None :
            self._name = pathlib.Path(__file__).name.split('.')[0]
        self._logger_obj = logging.getLogger(self._name)
        self._logger_obj.setLevel(logging.DEBUG)
        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(level)
        streamhandler.setFormatter(self.formatter)
        self._logger_obj.addHandler(streamhandler)
        if filepath is not None :
            self.add_file_handler(filepath)

    #function to add a filehandler to the logger
    def add_file_handler(self,filepath,level=logging.INFO) :
        filehandler = logging.FileHandler(filepath)
        filehandler.setLevel(level)
        filehandler.setFormatter(self.formatter)
        self._logger_obj.addHandler(filehandler)

    #functions for logging different levels of messages

    def debug(self,msg,*args,**kwargs) :
        self._logger_obj.debug(msg,*args,**kwargs)
    
    def info(self,msg,*args,**kwargs) :
        self._logger_obj.info(msg,*args,**kwargs)
    
    def warning(self,msg,*args,**kwargs) :
        if not msg.startswith('WARNING:') :
            msg = f'WARNING: {msg}'
        self._logger_obj.warning(msg)

    #function to log an error message and optionally raise an exception with the same message

    def error(self,msg,exception_type=None,*args,**kwargs) :
        if not msg.startswith('ERROR:') :
            msg = f'ERROR: {msg}'
        self._logger_obj.error(msg,*args,**kwargs)
        if exception_type is not None :
            raise exception_type(msg)

