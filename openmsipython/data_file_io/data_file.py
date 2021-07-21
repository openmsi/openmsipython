#imports
import pathlib
from ..utilities.logging import Logger
from ..utilities.my_base_class import MyBaseClass

class DataFile(MyBaseClass) :
    """
    Base class for representing a single data file
    """

    #################### PROPERTIES ####################

    @property
    def filepath(self):
        return self.__filepath
    @property
    def filename(self):
        return self.__filename
    @property
    def logger(self):
        return self.__logger

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,filepath,**kwargs) :
        """
        filepath = path to the file
        
        Possible keyword arguments:
        logger    = the logger object for this file's messages to use (a new one will be created if none is supplied)
        """
        self.__filepath = filepath.resolve()
        self.__filename = self.__filepath.name
        self.__logger = kwargs.get('logger')
        if self.__logger is None :
            self.__logger = Logger(pathlib.Path(__file__).name.split('.')[0])
