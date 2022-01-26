#imports
import pathlib
from openmsipython.shared.config import UTIL_CONST
from openmsipython.data_file_io.config import RUN_OPT_CONST

class TestRoutineConstants :
    """
    constants used in running tests
    """

    @property
    def TEST_CONFIG_FILE_PATH(self) : # The path to the Kafka config file to use
        return (UTIL_CONST.CONFIG_FILE_DIR / f'{RUN_OPT_CONST.DEFAULT_CONFIG_FILE}{UTIL_CONST.CONFIG_FILE_EXT}').resolve()
    @property
    def TEST_CONFIG_FILE_PATH_ENCRYPTED(self) : # Same as above except it includes a node_id to test encryption
        return (UTIL_CONST.CONFIG_FILE_DIR / f'test_encrypted{UTIL_CONST.CONFIG_FILE_EXT}').resolve()
    @property
    def PROD_CONFIG_FILE_PATH(self) : # The path to the "prod" Kafka config file to use in making sure that the prod environment variables are not set
        return (UTIL_CONST.CONFIG_FILE_DIR / f'prod{UTIL_CONST.CONFIG_FILE_EXT}').resolve()
    @property
    def FAKE_PROD_CONFIG_FILE_PATH(self) : # The path to the "prod" Kafka config file to use in making sure that the prod environment variables are not set
        return (self.TEST_DATA_DIR_PATH / f'fake_prod{UTIL_CONST.CONFIG_FILE_EXT}').resolve()
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
    def TEST_WATCHED_DIR_PATH_ENCRYPTED(self) : #same as above except for the encrypted tests
        return pathlib.Path(__file__).parent.parent / 'test_watched_dir_encrypted'
    @property
    def TEST_RECO_DIR_PATH(self) : # Path to the directory where consumed files should be reconstructed
        return pathlib.Path(__file__).parent.parent / 'test_reco'
    @property
    def TEST_RECO_DIR_PATH_ENCRYPTED(self) : # same as above except for encrypted tests
        return pathlib.Path(__file__).parent.parent / 'test_reco_encrypted'
    @property
    def FILEMAKER_RECORD_PICKLE_FILENAME(self) : # path to the pickle file holding a bunch of mocked FileMaker records
        return 'filemaker_records_for_testing.pickle'
    @property
    def LASER_SHOCK_DATA_MODEL_OUTPUT_DIRNAME(self) : 
        # path to the directory where the laser shock GEMD output files should go
        return 'laser_shock_data_model_output'
    
TEST_CONST=TestRoutineConstants()