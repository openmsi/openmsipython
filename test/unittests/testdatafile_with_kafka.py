#imports
from config import TEST_CONST
from openmsipython.data_file_io.data_file import UploadDataFile
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.utilities.logging import Logger
import unittest, pathlib, logging

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestDataFileWithKafka(unittest.TestCase) :
    """
    Class for testing DataFile functions that interface with the Kafka cluster
    """

    def setUp(self) :
        self.datafile = UploadDataFile(TEST_CONST.TEST_DATA_FILE_PATH,rootdir=TEST_CONST.TEST_DATA_FILE_ROOT_DIR_PATH,logger=LOGGER)

    def test_upload_whole_file(self) :
        #just need to make sure this function runs without throwing any errors
        self.datafile.upload_whole_file(TEST_CONST.TEST_CONFIG_FILE_PATH,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,
                                        n_threads=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                        chunk_size=RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
