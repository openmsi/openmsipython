#imports
import unittest, platform, shutil
from subprocess import check_output
from openmsipython.services.config import SERVICE_CONST
from openmsipython.services.utilities import get_os_name
from openmsipython.services.install_service import install_service
from openmsipython.services.manage_service import start_service, service_status, stop_service, remove_service
from config import TEST_CONST

class TestLinuxServices(unittest.TestCase) :
    """
    Class for testing that Services can be installed/started/stopped/removed without any errors on Linux OS
    """

    @unittest.skipIf(platform.system()!='Linux' or check_output(['ps','--no-headers','-o','comm','1'])!='systemd',
                     'test requires systemd running on Linux')
    def test_install_start_stop_remove_linux_services(self) :
        """
        Make sure every possible Linux service can be installed, started, checked, stopped, and removed
        """
        self.assertTrue(len(SERVICE_CONST.AVAILABLE_SERVICES)>0)
        dirs_to_delete = [TEST_CONST.TEST_DIR_SERVICES_TEST]
        for dirpath in dirs_to_delete :
            if not dirpath.is_dir() :
                dirpath.mkdir(parents=True)
        try :
            argslists_by_class_name = {
                'UploadDataFile':[TEST_CONST.TEST_DATA_FILE_PATH,],
                'DataFileUploadDirectory':[TEST_CONST.TEST_DIR_SERVICES_TEST,],
                'DataFileDownloadDirectory':[TEST_CONST.TEST_DIR_SERVICES_TEST,],
                'LecroyFileUploadDirectory':[TEST_CONST.TEST_DIR_SERVICES_TEST,
                                             '--config',TEST_CONST.TEST_CONFIG_FILE_PATH,
                                             '--topic_name','test_pdv_plots'],
                'PDVPlotMaker':[TEST_CONST.TEST_DIR_SERVICES_TEST,
                                '--config',TEST_CONST.TEST_CONFIG_FILE_PATH,
                                '--topic_name','test_pdv_plots',
                                '--consumer_group_id','create_new'],
                'OSNStreamProcessor':['phy210127-bucket01',
                                      '--logger_file',TEST_CONST.TEST_DIR_SERVICES_TEST/'test_osn_stream_processor.log',
                                      '--config',TEST_CONST.TEST_CONFIG_FILE_PATH_OSN,
                                      '--topic_name','osn_test',
                                      '--consumer_group_id','create_new'],
            }
            operating_system = get_os_name()
            for sd in SERVICE_CONST.AVAILABLE_SERVICES :
                service_class_name = sd['class'].__name__
                if service_class_name not in argslists_by_class_name.keys() :
                    raise ValueError(f'ERROR: no arguments to use found for class "{service_class_name}"!')
                service_name = service_class_name+'_test'
                argslist_to_use = []
                for arg in argslists_by_class_name[service_class_name] :
                    argslist_to_use.append(str(arg))
                install_service(service_class_name,service_name,argslist_to_use,operating_system,interactive=False)
                start_service(service_name,operating_system)
                service_status(service_name,operating_system)
                stop_service(service_name,operating_system)
                remove_service(service_name,operating_system)
                self.assertFalse((SERVICE_CONST.DAEMON_SERVICE_DIR/f'{service_name}.service').exists())
        except Exception as e :
            raise e
        finally :
            for dirpath in dirs_to_delete :
                if dirpath.is_dir() :
                    shutil.rmtree(dirpath)
        for dirpath in dirs_to_delete :
            self.assertFalse(dirpath.is_dir())
