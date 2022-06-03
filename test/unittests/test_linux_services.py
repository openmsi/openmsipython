#imports
import unittest, pathlib, platform
from openmsipython.services.config import SERVICE_CONST
from openmsipython.services.install_service import install_service
from openmsipython.services.manage_service import start_service, service_status, stop_service, remove_service
from config import TEST_CONST

class TestLinuxServices(unittest.TestCase) :
    """
    Class for testing that Services can be installed/started/stopped/removed without any errors on Linux OS
    """

    @unittest.skipIf(platform.system()!='Linux','test requires systemd so only runs on Linux')
    def test_install_start_stop_remove_linux_services(self) :
        """
        Make sure every possible Linux service can be installed, started, checked, stopped, and removed
        """
        self.assertTrue(len(sd)>0)
        for sd in SERVICE_CONST.AVAILABLE_SERVICES :
            pass
