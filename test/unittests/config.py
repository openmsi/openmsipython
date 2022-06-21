#imports
import pathlib

class TestRoutineConstants :
    """
    constants used in running tests
    """
    @property
    def TEST_TOPIC_NAMES(self) :
        return {'test_pdv_plots':'test_pdv_plots',}
    @property
    def TEST_DIR_PATH(self) :
        return pathlib.Path(__file__).parent.parent
    @property
    def TEST_DATA_DIR_PATH(self) : #path to the test data directory
        return self.TEST_DIR_PATH / 'data'
    @property
    def TEST_CONFIG_FILE_PATH(self) : # The path to the Kafka config file to use
        return (self.TEST_DATA_DIR_PATH/'test.config').resolve()
    @property
    def TEST_DATA_FILE_SUB_DIR_NAME(self) : #path to the test data directory
        return 'test_file_sub_dir_pdv'
    @property
    def TEST_LECROY_DATA_FILE_NAME(self) : # Name of the test Lecroy data file for PDV tests
        return 'F2--20210529--00013.txt'
    @property
    def TEST_LECROY_DATA_FILE_PATH(self) : # Path to the test Lecroy data file
        return self.TEST_DATA_DIR_PATH / self.TEST_LECROY_DATA_FILE_NAME
    @property
    def TEST_WATCHED_DIR_PATH_PDV(self) : #path to the "watched" directory to use in testing PDV plots
        return pathlib.Path(__file__).parent.parent / 'test_watched_dir_pdv'
    @property
    def TEST_RECO_DIR_PATH_PDV(self) : # Path to the directory where consumed files will be reconstructed for PDV tests
        return self.TEST_DIR_PATH / 'test_reco'
    @property
    def FILEMAKER_RECORD_PICKLE_FILENAME(self) : # path to the pickle file holding a bunch of mocked FileMaker records
        return 'filemaker_records_for_testing.pickle'
    @property
    def LASER_SHOCK_DATA_MODEL_OUTPUT_DIRNAME(self) : 
        # path to the directory where the laser shock GEMD output files should go
        return 'laser_shock_data_model_output'
    
TEST_CONST=TestRoutineConstants()