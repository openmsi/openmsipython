#imports
import unittest, pathlib, importlib, filecmp, os, logging
from openmsipython.utilities.logging import Logger
from openmsipython.services.config import SERVICE_CONST
from openmsipython.services.utilities import find_install_NSSM
from openmsipython.services.install_service import write_executable_file
from config import TEST_CONST

#constants
TEST_SERVICE_NAME = 'DataFileUploadDirectoryService'
TEST_SERVICE_EXECUTABLE_ARGSLIST = ['test_upload']
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.INFO)

class TestServiceUtilities(unittest.TestCase) :
    """
    Class for testing that several utilities used by the Service management code are behaving as expected
    """

    def test_some_configs(self) :
        """
        Make sure that some config variables can be created successfully
        """
        self.assertFalse(SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file())
        for sd in SERVICE_CONST.AVAILABLE_SERVICES :
            _ = importlib.import_module(sd['filepath'])
        #the command below explicitly creates a file but that file should be ignored in the repo
        SERVICE_CONST.LOGGER.info('testing')

    def test_write_executable_file(self) :
        """
        Make sure an executable file is written to the expected location with the expected format
        """
        #the test below does create a file but that file should be ignored in the repo
        LOGGER.set_stream_level(logging.INFO)
        LOGGER.info('testing')
        test_exec_fp = pathlib.Path(__file__).parent.parent.parent/'openmsipython'/'services'
        test_exec_fp = test_exec_fp/'working_dir'/f'{TEST_SERVICE_NAME}{SERVICE_CONST.SERVICE_EXECUTABLE_NAME_STEM}'
        write_executable_file(TEST_SERVICE_NAME,TEST_SERVICE_EXECUTABLE_ARGSLIST,test_exec_fp,LOGGER)
        LOGGER.info(f'Will search directory at {test_exec_fp.parent}')
        for fp in test_exec_fp.parent.glob('*') :
            LOGGER.info(f'Found file {fp}')
        self.assertTrue(test_exec_fp.is_file())
        ref_exec_fp = TEST_CONST.TEST_DATA_DIR_PATH/test_exec_fp.name
        self.assertTrue(ref_exec_fp.is_file())
        self.assertTrue(filecmp.cmp(test_exec_fp,ref_exec_fp,shallow=False))

    @unittest.skipIf(os.name!='nt','test requires Powershell and so only runs on Windows')
    def test_download_NSSM(self) :
        """
        Make sure NSSM can be downloaded to the expected location
        """
        self.assertFalse(SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file())
        #the command below does leave a file in the repo but it should be ignored
        find_install_NSSM()
        self.assertTrue(SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file())
