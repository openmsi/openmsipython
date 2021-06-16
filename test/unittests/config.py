#constants used in running tests

#imports
from openmsipython.utilities.argument_parsing import CONFIG_FILE_DIR, CONFIG_FILE_EXT
from openmsipython.data_file_io.config import RUN_OPT_CONST
import pathlib

class TestRoutineConstants :

    @property
    def TEST_CONFIG_FILE_PATH(self) : # The path to the Kafka config file to use
        return (CONFIG_FILE_DIR / f'{RUN_OPT_CONST.DEFAULT_CONFIG_FILE}{CONFIG_FILE_EXT}').resolve()
    @property
    def PROD_CONFIG_FILE_PATH(self) : # The path to the "prod" Kafka config file to use in making sure that the prod environment variables are not set
        return (CONFIG_FILE_DIR / f'prod{CONFIG_FILE_EXT}').resolve()
    @property
    def FAKE_PROD_CONFIG_FILE_PATH(self) : # The path to the "prod" Kafka config file to use in making sure that the prod environment variables are not set
        return (self.TEST_DATA_DIR_PATH / f'fake_prod{CONFIG_FILE_EXT}').resolve()
    @property
    def TEST_CONFIG_FILE_PATH_NO_SERIALIZATION(self) : # Same as above except it's the config file that doesn't have the serialization stuff in it
        return (CONFIG_FILE_DIR / 'test_no_serialization.config').resolve()
    @property
    def TEST_DATA_DIR_PATH(self) : #path to the test data directory
        return pathlib.Path(__file__).parent.parent / 'data'
    @property
    def TEST_DATA_FILE_ROOT_DIR_NAME(self) : #path to the test data directory
        return 'test_file_root_dir'
    @property
    def TEST_DATA_FILE_SUB_DIR_NAME(self) : #path to the test data directory
        return 'test_file_sub_dir'
    @property 
    def TEST_DATA_FILE_NAME(self) : #name of the test data file
        return '1a0ceb89-b5f0-45dc-9c12-63d3020e2217.dat'
    @property
    def TEST_DATA_FILE_ROOT_DIR_PATH(self) : # Path to the test data file
        return self.TEST_DATA_DIR_PATH / self.TEST_DATA_FILE_ROOT_DIR_NAME
    @property
    def TEST_DATA_FILE_PATH(self) : # Path to the test data file
        return self.TEST_DATA_DIR_PATH / self.TEST_DATA_FILE_ROOT_DIR_NAME / self.TEST_DATA_FILE_SUB_DIR_NAME/ self.TEST_DATA_FILE_NAME
    @property
    def TEST_WATCHED_DIR_PATH(self) : #path to the "watched" directory to use in testing DataFileDirectory etc.
        return pathlib.Path(__file__).parent.parent / 'test_watched_dir'
    @property
    def TEST_RECO_DIR_PATH(self) : # Path to the test data file
        return pathlib.Path(__file__).parent.parent / 'test_reco'
    
TEST_CONST=TestRoutineConstants()