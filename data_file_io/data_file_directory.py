#imports
from .data_file import DataFile
from ..my_kafka.my_producers import TutorialClusterProducer
from ..utilities.misc import populated_kwargs
from ..utilities.logging import Logger
from ..utilities.config import DATA_FILE_HANDLING_CONST, RUN_OPT_CONST, TUTORIAL_CLUSTER_CONST
from confluent_kafka import Producer
from queue import Queue
from threading import Thread, Lock
from contextlib import nullcontext
from hashlib import sha512
import os

# DataFileDirectory Class
class DataFileDirectory() :
    """
    Class for representing a directory holding data files
    Can be used to listen for new files to be added and upload them as they are
    """
    def __init__(self,dirpath,**kwargs) :
        """
        dirpath = path to the directory to listen in on
        
        Possible keyword arguments:
        logger = the logger object to use (a new one will be created if none is supplied)
        """
        self._dirpath = dirpath
        self._logger = kwargs.get('logger')
        if self._logger is None :
            self._logger = Logger(os.path.basename(__file__).split('.')[0])

    #################### PUBLIC FUNCTIONS ####################

    def upload_files_as_added(self,**kwargs) :
        """
        Listen for new files to be added to the directory. Any newly added files will be chunked and produced as mesages to the topic.

        Possible keyword arguments:
        n_threads  = the number of threads to run at once during uploading
        chunk_size = the size of each file chunk in bytes
        producer   = the producer object to use
        topic_name = the name of the topic to use
        """
        #set the important variables
        kwargs = populated_kwargs(kwargs,
                                  {'n_threads': RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                   'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                   'producer': (TutorialClusterProducer(),Producer),
                                   'topic_name': TUTORIAL_CLUSTER_CONST.LECROY_FILE_TOPIC_NAME
                                  },self._logger)
        
