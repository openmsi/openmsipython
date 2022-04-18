#imports
import unittest, pathlib, importlib#, os
from openmsipython.services.config import SERVICE_CONST
from openmsipython.services.utilities import find_install_NSSM
from openmsipython.services.install_service import write_executable_file
from config import TEST_CONST

#constants
TEST_SERVICE_NAME = 'DataFileUploadDirectoryService'
TEST_SERVICE_EXECUTABLE_ARGSLIST = ['test_upload']

class TestServiceUtilities(unittest.TestCase) :
    """
    Class for testing that several utilities used by the Service management code are behaving as expected
    """

    def test_some_configs(self) :
        """
        Make sure that some config variables can be created successfully
        """
        #self.assertFalse(SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file())
        for sd in SERVICE_CONST.AVAILABLE_SERVICES :
            _ = importlib.import_module(sd['filepath'])
        #the command below explicitly creates a file but that file should be ignored in the repo
        SERVICE_CONST.LOGGER.info('testing')

    def test_write_executable_file(self) :
        """
        Make sure an executable file is written to the expected location with the expected format
        """
        #the test below does create a file but that file should be ignored in the repo
        test_exec_fp = pathlib.Path(__file__).parent.parent.parent/'openmsipython'/'services'
        test_exec_fp = test_exec_fp/'working_dir'/f'{TEST_SERVICE_NAME}{SERVICE_CONST.SERVICE_EXECUTABLE_NAME_STEM}'
        write_executable_file(TEST_SERVICE_NAME,TEST_SERVICE_EXECUTABLE_ARGSLIST,test_exec_fp)
        self.assertTrue(test_exec_fp.is_file())
        with open(test_exec_fp,'r') as test_fp :
            test_lines = test_fp.readlines()
        ref_exec_fp = TEST_CONST.TEST_DATA_DIR_PATH/test_exec_fp.name
        self.assertTrue(ref_exec_fp.is_file())
        with open(ref_exec_fp,'r') as ref_fp :
            ref_lines = ref_fp.readlines()
        for test_line,ref_line in zip(test_lines,ref_lines) :
            if ref_line.lstrip().startswith('output_filepath = ') :
                continue
            else :
                self.assertTrue(test_line==ref_line)

    #@unittest.skipIf(os.name!='nt','test requires Powershell and so only runs on Windows')
    @unittest.skip("Skipping NSSM download test because it's finicky")
    def test_download_NSSM(self) :
        """
        Make sure NSSM can be downloaded to the expected location
        """
        self.assertFalse(SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file())
        #the command below does leave a file in the repo but it should be ignored
        find_install_NSSM()
        self.assertTrue(SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file())
