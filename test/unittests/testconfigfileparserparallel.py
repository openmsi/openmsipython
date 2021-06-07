#imports
from config import TEST_CONST
from openmsipython.utilities.config_file_parser import ConfigFileParser
from openmsipython.utilities.logging import Logger
from random import choices
import os, unittest, logging, configparser, string, pathlib

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestConfigFileParser(unittest.TestCase) :
    """
    Class for testing ConfigFileParser functions
    """

    def setUp(self) :
        self.cfp = ConfigFileParser(TEST_CONST.TEST_CONFIG_FILE_PATH,logger=LOGGER)
        self.testconfigparser = configparser.ConfigParser()
        self.testconfigparser.read(TEST_CONST.TEST_CONFIG_FILE_PATH)

    def test_available_group_names(self) :
        self.assertEqual(self.cfp.available_group_names,self.testconfigparser.sections())

    def test_get_config_dict_for_groups(self) :
        if len(self.testconfigparser.sections())<2 :
            raise RuntimeError(f'ERROR: config file used for testing ({TEST_CONST.TEST_CONFIG_FILE_PATH}) does not contain enough sections to test with!')
        for group_name in self.testconfigparser.sections() :
            group_ref_dict = dict(self.testconfigparser[group_name])
            for k,v in group_ref_dict.items() :
                if v.startswith('$') :
                    group_ref_dict[k] = os.path.expandvars(v)
            self.assertEqual(self.cfp.get_config_dict_for_groups(group_name),group_ref_dict)
        all_sections_dict = {}
        for group_name in self.testconfigparser.sections() :
            all_sections_dict = {**all_sections_dict,**(dict(self.testconfigparser[group_name]))}
            for k,v in all_sections_dict.items() :
                if v.startswith('$') :
                    all_sections_dict[k] = os.path.expandvars(v)
        self.assertEqual(self.cfp.get_config_dict_for_groups(self.testconfigparser.sections()),all_sections_dict)
        random_section_name = ''.join(choices(string.ascii_letters,k=10))
        while random_section_name in self.cfp.available_group_names :
            random_section_name = string.ascii_letters
        LOGGER.set_stream_level(logging.INFO)
        LOGGER.info('\nExpecting two errors below:')
        LOGGER.set_stream_level(logging.ERROR)
        with self.assertRaises(ValueError) :
            _ = self.cfp.get_config_dict_for_groups(random_section_name)
        with self.assertRaises(ValueError) :
            _ = self.cfp.get_config_dict_for_groups([self.testconfigparser.sections()[0],random_section_name])
