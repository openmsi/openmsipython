#imports
import pathlib
from ..utilities.misc import populated_kwargs
from ..utilities.logging import Logger
from ..utilities.my_base_class import MyBaseClass

class DataFileDirectory(MyBaseClass) :
    """
    Base class representing any directory holding data files
    """

    #################### PROPERTIES ####################

    @property
    def dirpath(self) :
        return self.__dirpath
    @property
    def logger(self) :
        return self.__logger

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,dirpath,*args,**kwargs) :
        """
        dirpath = path to the directory 
        
        Possible keyword arguments:
        logger = the logger object to use (a new one will be created if none is supplied)
        """
        self.__dirpath = dirpath.resolve()
        self.__logger = kwargs.get('logger')
        if self.__logger is None :
            self.__logger = Logger(pathlib.Path(__file__).name.split('.')[0])
        self.data_files_by_path = {}
        kwargs = populated_kwargs(kwargs,{'logger':self.__logger})
        super().__init__(*args,**kwargs)
