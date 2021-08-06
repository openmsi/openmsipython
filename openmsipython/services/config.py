#imports
import pathlib, importlib, pkg_resources
from inspect import isclass
from ..utilities.runnable import Runnable

class ServicesConstants :
    """
    Constants for working with services
    """
    @property
    def AVAILABLE_SERVICES(self) :
        service_dicts = []
        for script in pkg_resources.iter_entry_points('console_scripts') :
            if script.dist.key == 'openmsipython' :
                service_dict = {}
                scriptstr = str(script)
                cmd = (scriptstr.split())[0]
                path = ((scriptstr.split())[2].split(':'))[0]
                funcname = (((scriptstr.split())[2]).split(':'))[1]
                module = importlib.import_module(path)
                run_classes = [getattr(module,x) for x in dir(module) if x!='Runnable' and
                               isclass(getattr(module,x)) and issubclass(getattr(module,x),Runnable)]
                top_classes = [c for c in run_classes if any([issubclass(c,_) for _ in run_classes if _!=c])]
                print(f'top classes for cmd {cmd}  = {run_classes}')
        return service_dicts
    @property
    def NSSM_DOWNLOAD_URL(self) :
        return 'https://nssm.cc/release/nssm-2.24.zip' # The URL to use for downloading NSSM when needed
    @property
    def NSSM_EXECUTABLE_PATH(self) :
        return pathlib.Path(__file__.parent) / 'working_dir' / 'nssm.exe'
    @property
    def SERVICE_EXECUTABLE_NAME_STEM(self) :
        return '_python_executable.py'

SERVICE_CONST = ServicesConstants()