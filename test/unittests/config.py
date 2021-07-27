#imports
from openmsipython.utilities.config import UTIL_CONST
from openmsipython.data_file_io.config import RUN_OPT_CONST
import pathlib

class TestRoutineConstants :
    """
    constants used in running tests
    """

    @property
    def TEST_CONFIG_FILE_PATH(self) : # The path to the Kafka config file to use
        return (UTIL_CONST.CONFIG_FILE_DIR / f'{RUN_OPT_CONST.DEFAULT_CONFIG_FILE}{UTIL_CONST.CONFIG_FILE_EXT}').resolve()
    @property
    def PROD_CONFIG_FILE_PATH(self) : # The path to the "prod" Kafka config file to use in making sure that the prod environment variables are not set
        return (UTIL_CONST.CONFIG_FILE_DIR / f'prod{UTIL_CONST.CONFIG_FILE_EXT}').resolve()
    @property
    def FAKE_PROD_CONFIG_FILE_PATH(self) : # The path to the "prod" Kafka config file to use in making sure that the prod environment variables are not set
        return (self.TEST_DATA_DIR_PATH / f'fake_prod{UTIL_CONST.CONFIG_FILE_EXT}').resolve()
    @property
    def TEST_CONFIG_FILE_PATH_NO_SERIALIZATION(self) : # Same as above except it's the config file that doesn't have the serialization stuff in it
        return (UTIL_CONST.CONFIG_FILE_DIR / 'test_no_serialization.config').resolve()
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
    def TEST_DATA_FILE_2_NAME(self) : #name of a second test data file
        return '4ceee043-0b99-4f49-8527-595d93ddc487.dat'
    @property
    def TEST_DATA_FILE_ROOT_DIR_PATH(self) : # Path to the test data file
        return self.TEST_DATA_DIR_PATH / self.TEST_DATA_FILE_ROOT_DIR_NAME
    @property
    def TEST_DATA_FILE_PATH(self) : # Path to the test data file
        return self.TEST_DATA_DIR_PATH / self.TEST_DATA_FILE_ROOT_DIR_NAME / self.TEST_DATA_FILE_SUB_DIR_NAME/ self.TEST_DATA_FILE_NAME
    @property
    def TEST_DATA_FILE_2_PATH(self) : # Path to the second test data file
        return self.TEST_DATA_DIR_PATH / self.TEST_DATA_FILE_2_NAME
    @property
    def TEST_LECROY_DATA_FILE_NAME(self) : # Name of the test Lecroy data file
        return 'F2--20210529--00013.txt'
    @property
    def TEST_LECROY_DATA_FILE_PATH(self) : # Path to the test Lecroy data file
        return self.TEST_DATA_DIR_PATH / self.TEST_LECROY_DATA_FILE_NAME
    @property
    def TEST_WATCHED_DIR_PATH(self) : #path to the "watched" directory to use in testing DataFileDirectory etc.
        return pathlib.Path(__file__).parent.parent / 'test_watched_dir'
    @property
    def TEST_RECO_DIR_PATH(self) : # Path to the test data file
        return pathlib.Path(__file__).parent.parent / 'test_reco'
    
TEST_CONST=TestRoutineConstants()