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
    def TEST_CONFIG_FILE_PATH_NO_SERIALIZATION(self) : # Same as above except it's the config file that doesn't have the serialization stuff in it
        return (CONFIG_FILE_DIR / 'test_no_serialization.config').resolve()
    @property
    def TEST_DATA_FILE_PATH(self) : # Path to the test data file
        return pathlib.Path(__file__).parent.parent / 'data' / '1a0ceb89-b5f0-45dc-9c12-63d3020e2217.dat'
    @property
    def TEST_RECO_DIR_PATH(self) : # Path to the test data file
        return pathlib.Path(__file__).parent.parent / 'test_reco'
    
TEST_CONST=TestRoutineConstants()