#imports
import pkg_resources, subprocess, unittest

class TestConsoleScripts(unittest.TestCase):
    
    def testConsoleScripts(self):
        """
        Make sure console scripts defined in setup.py exist and that their imports work
        """
        for script in pkg_resources.iter_entry_points('console_scripts') :
            if script.dist.key == 'openmsipython' :
                with self.subTest(script=script.name):
                    try:
                        subprocess.check_output([script.name, '--help'],stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as e:
                        raise RuntimeError(f'ERROR: test for console script "{script.name}" failed with output:\n{e.output.decode()}')
