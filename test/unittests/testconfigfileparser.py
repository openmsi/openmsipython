#imports
from openmsipython.utilities.config_file_parser import ConfigFileParser
from openmsipython.utilities.logging import Logger
from openmsipython.utilities.argument_parsing import CONFIG_FILE_DIR, CONFIG_FILE_EXT
from openmsipython.data_file_io.config import RUN_OPT_CONST
import unittest, logging, configparser

#constants
TEST_CONFIG_FILE_PATH = (CONFIG_FILE_DIR / f'{RUN_OPT_CONST.DEFAULT_CONFIG_FILE}{CONFIG_FILE_EXT}').resolve()
LOGGER = Logger('test',logging.ERROR)

class TestConfigFileParser(unittest.TestCase) :
    """
    Class for testing ConfigFileParser functions
    """

    def setUp(self) :
        self.cfp = ConfigFileParser(TEST_CONFIG_FILE_PATH,logger=LOGGER)
        self.testconfigparser = configparser.ConfigParser()
        self.testconfigparser.read(TEST_CONFIG_FILE_PATH)

    def test_available_group_names(self) :
        self.assertEqual(self.cfp.available_group_names,self.testconfigparser.sections())

    def test_get_config_dict_for_groups(self) :
        if len(self.testconfigparser.sections())<2 :
            raise RuntimeError(f'ERROR: config file used for testing ({TEST_CONFIG_FILE_PATH}) does not contain enough sections to test with!')
        for group_name in self.testconfigparser.sections() :
            self.assertEqual(self.cfp.get_config_dict_for_groups(group_name),dict(self.testconfigparser[group_name]))
        all_sections_dict = {}
        for group_name in self.testconfigparser.sections() :
            all_sections_dict = {**all_sections_dict,**(dict(self.testconfigparser[group_name]))}
        self.assertEqual(self.cfp.get_config_dict_for_groups(self.testconfigparser.sections()),all_sections_dict)
