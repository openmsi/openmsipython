#imports
import logging, pathlib

class Logger :
    """
    Class for a general logger. Logs messages and raises exceptions
    """

    @property
    def formatter(self):
        return logging.Formatter('[%(name)s at %(asctime)s] %(message)s','%Y-%m-%d %H:%M:%S')

    def __init__(self,name=None,streamlevel=logging.DEBUG,filepath=None,filelevel=logging.INFO) :
        """
        name = the name for this logger to use (probably something like the top module that owns it)
        """
        self._name = name
        if self._name is None :
            self._name = pathlib.Path(__file__).name.split('.')[0]
        self._logger_obj = logging.getLogger(self._name)
        self._logger_obj.setLevel(logging.DEBUG)
        self._streamhandler = logging.StreamHandler()
        self._streamhandler.setLevel(streamlevel)
        self._streamhandler.setFormatter(self.formatter)
        self._logger_obj.addHandler(self._streamhandler)
        self._filehandler = None
        if filepath is not None :
            self.add_file_handler(filepath)

    #set the level of the underlying logger
    def set_level(self,level) :
        self._logger_obj.setLevel(level)
    #set the level of the streamhandler
    def set_stream_level(self,level) :
        self._streamhandler.setLevel(level)
    #set the level of the filehandler
    def set_file_level(self,level) :
        if self._filehandler is None :
            raise RuntimeError(f'ERROR: Logger with name {self._name} does not have a filehandler set but set_file_level was called!')
        self._filehandler.setLevel(level)

    #add a filehandler to the logger
    def add_file_handler(self,filepath,level=logging.INFO) :
        self._filehandler = logging.FileHandler(filepath)
        self._filehandler.setLevel(level)
        self._filehandler.setFormatter(self.formatter)
        self._logger_obj.addHandler(self._filehandler)

    #methods for logging different levels of messages

    def debug(self,msg,*args,**kwargs) :
        self._logger_obj.debug(msg,*args,**kwargs)
    
    def info(self,msg,*args,**kwargs) :
        self._logger_obj.info(msg,*args,**kwargs)
    
    def warning(self,msg,*args,**kwargs) :
        if not msg.startswith('WARNING:') :
            msg = f'WARNING: {msg}'
        self._logger_obj.warning(msg)

    #log an error message and optionally raise an exception with the same message
    def error(self,msg,exception_type=None,*args,**kwargs) :
        if not msg.startswith('ERROR:') :
            msg = f'ERROR: {msg}'
        self._logger_obj.error(msg,*args,**kwargs)
        if exception_type is not None :
            raise exception_type(msg)

