#imports
import sys, os, pathlib, textwrap, shutil, ctypes.util
from abc import abstractmethod
from subprocess import CalledProcessError
from ..shared.argument_parsing import MyArgumentParser
from ..shared.config_file_parser import ConfigFileParser
from ..shared.logging import LogOwner
from ..shared.has_argument_parser import HasArgumentParser
from .config import SERVICE_CONST
from .utilities import get_os_name, test_python_code, set_env_vars, remove_env_var, run_cmd_in_subprocess

################################################################################
################################## BASE CLASS ##################################
################################################################################

class ServiceManagerBase(LogOwner,HasArgumentParser) :
    """
    Base class for working with Services in general
    """

    #################### CLASS METHODS ####################
    
    @classmethod
    def get_argument_parser(cls,install_or_manage) :
        parser = MyArgumentParser()
        if install_or_manage=='install' :
            #subparsers from the classes that could be run
            subp_desc = 'The name of a runnable class to install as a service must be given as the first argument. '
            subp_desc = 'Adding one of these class names to the command line along with "-h" will show additional help.'
            parser.add_subparsers(description=subp_desc,required=True,dest='service_class_name')
            for service_dict in SERVICE_CONST.AVAILABLE_SERVICES :
                parser.add_subparser_arguments_from_class(service_dict['class'],addl_args=['optional_service_name'])
        elif install_or_manage=='manage' :
            parser.add_arguments('service_name','run_mode','remove_env_vars','remove_nssm')
        else :
            errmsg =  'ERROR: must call get_argument_parser with either "install" or "manage", '
            errmsg+= f'not "{install_or_manage}"!'
            raise ValueError(errmsg)
        return parser

    #################### PROPERTIES ####################

    @property
    def env_var_names(self) :
        """
        Names of the environment variables used by the service
        """
        #get the names of environment variables from the command line and config file
        if self.argslist is not None and self.service_dict is not None :
            for arg in self.argslist :
                if arg.startswith('$') :
                    yield arg
            p = self.service_dict['class'].get_argument_parser()
            argsdests = [action.dest for action in p._actions]
            if 'config' in argsdests :
                pargs = p.parse_args(args=self.argslist)
                cfp = ConfigFileParser(pargs.config,logger=SERVICE_CONST.LOGGER)
                for evn in cfp.env_var_names :
                    yield evn

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,service_name,*args,service_class_name=None,argslist=None,interactive=None,**kwargs) :
        super().__init__(*args,**kwargs)
        self.service_name = service_name
        self.service_class_name = service_class_name
        if self.service_class_name is not None :
            #set the dictionary with details about the program that will run
            service_dict = [sd for sd in SERVICE_CONST.AVAILABLE_SERVICES if sd['script_name']==service_class_name]
            if len(service_dict)!=1 :
                errmsg = f'ERROR: could not find the Service dictionary for {service_name} '
                errmsg+= f'(a {service_class_name} program)! service_dict = {service_dict}'
                self.logger.error(errmsg,RuntimeError)
            self.service_dict = service_dict[0]
        else :
            self.service_dict = None
        self.argslist = argslist
        self.interactive = interactive
        self.exec_fp = SERVICE_CONST.WORKING_DIR/f'{self.service_name}{SERVICE_CONST.SERVICE_EXECUTABLE_NAME_STEM}'
        self.env_var_filepath = SERVICE_CONST.WORKING_DIR/f'{self.service_name}_env_vars.txt'
    
    def install_service(self) :
        """
        Install the Service
        child classes should call this method to get the setup done before they do anything specific
        """
        #make sure the necessary information was supplied
        if self.service_class_name is None or self.service_dict is None or self.argslist is None :
            errmsg = 'ERROR: newly installing a Service requires that the class name and argslist are supplied!'
            self.logger.error(errmsg,RuntimeError)
        #set the environment variables
        must_rerun = set_env_vars(self.env_var_names,interactive=self.interactive)
        if must_rerun :
            msg = 'New values for environment variables have been set. '
            msg+= 'Please close this window and rerun InstallService so that their values get picked up.'
            self.logger.info(msg)
            sys.exit(0)
        #write out the environment variable file
        self._write_env_var_file()
        #write out the executable file
        self._write_executable_file()
        #install the service
        msg='Installing a'
        if self.service_class_name[0].lower() in ('a','e','i','o','u','y') :
            msg+='n'
        msg+=f' {self.service_class_name} program as "{self.service_name}" from executable at {self.exec_fp}...'
        self.logger.info(msg)

    def run_manage_command(self,run_mode,remove_env_vars=False,remove_nssm=False) :
        """
        Run one of the functions below according to the action given
        """
        if run_mode in ['start'] :
            self.start_service()
        if run_mode in ['status'] :
            self.service_status()
        if run_mode in ['stop','stop_and_remove'] :
            self.stop_service()
        if run_mode in ['remove','stop_and_remove'] :
            self.remove_service(remove_env_vars=remove_env_vars,remove_nssm=remove_nssm)

    @abstractmethod
    def start_service(self) :
        """
        start the Service
        not implemented in the base class
        """
        pass

    @abstractmethod
    def service_status(self) :
        """
        get the status of the service
        not implemented in the base class
        """
        pass

    @abstractmethod
    def stop_service(self) :
        """
        stop the Service
        not implemented in the base class
        """
        pass

    def remove_service(self,remove_env_vars=False) :
        """
        remove the Service
        child classes should call this after doing whatever they need to do to possibly remove environment variables
        """
        #remove the executable file
        if self.exec_fp.is_file() :
            self.exec_fp.unlink()
        #remove the environment variables that were set when the service was installed
        if remove_env_vars :
            try :
                for env_var_name in self.env_var_names :
                    remove_env_var(env_var_name)
                    self.logger.info(f'{env_var_name} environment variable successfully removed')
            except CalledProcessError :
                warnmsg = 'WARNING: failed to remove environment variables. You should remove any username/password '
                warnmsg+= 'environment variables manually even though the service is uninstalled!'
                self.logger.info(warnmsg)
        else :
            self.logger.info('Environment variables will be retained')
        #remove the actual environment variable file
        if self.env_var_filepath.is_file() :
            self.env_var_filepath.unlink()
        self.logger.info(f'Done removing {self.service_name}')

    #################### PRIVATE HELPER FUNCTIONS ####################
    
    def _write_executable_file(self,filepath=None) :
        """
        write out the executable python file that the service will actually be running
        """
        code = f'''\
            if __name__=='__main__' :
                try :
                    from {self.service_dict['filepath']} import {self.service_dict['func_name']}
                    {self.service_dict['func_name']}({self.argslist})
                except Exception :
                    import pathlib, traceback, datetime
                    output_filepath = pathlib.Path(r"{pathlib.Path().resolve()/'SERVICES_ERROR_LOG.txt'}")
                    with open(output_filepath,'a') as fp :'''
        code+=r'''
                        fp.write(f'{(datetime.datetime.now()).strftime("Error on %Y-%m-%d at %H:%M:%S")}. Exception:\n{traceback.format_exc()}')
                    import sys
                    sys.exit(1)
        '''
        if filepath is not None :
            warnmsg = f'WARNING: Services executable will be written to {filepath} instead of {self.exec_fp}'
            self.logger.warning(warnmsg)
            exec_fp = filepath
        else :
            exec_fp = self.exec_fp
        with open(exec_fp,'w') as fp :
            fp.write(textwrap.dedent(code))

    @abstractmethod
    def _write_env_var_file(self) :
        """
        Write and set permissions for the file holding the values of the environment variables needed by the Service
        returns True if a file was written, False if none needed
        not implemented in base class
        """
        pass

################################################################################
############################### WINDOWS SERVICES ###############################
################################################################################

class WindowsServiceManager(ServiceManagerBase) :
    """
    Class for working with Windows Services
    """

    @property
    def env_var_names(self):
        for evn in super().env_var_names :
            yield evn
        #get the names of environment variables from the env_var file
        if self.env_var_filepath.is_file() :
            with open(self.env_var_filepath,'r') as fp :
                lines = fp.readlines()
            for line in lines :
                try :
                    linestrip = line.strip()
                    if linestrip!='' :
                        yield linestrip
                except :
                    pass

    def install_service(self) :
        super().install_service()
        #if it doesn't exist there yet, copy the libsodium.dll file to C:\Windows\system32
        self.__copy_libsodium_dll_to_system32()
        #find or install NSSM to run the executable
        self.__find_install_NSSM()
        #run NSSM to install the service
        cmd = f'{SERVICE_CONST.NSSM_PATH} install {self.service_name} \"{sys.executable}\" \"{self.exec_fp}\"'
        run_cmd_in_subprocess(['powershell.exe',cmd],logger=self.logger)
        run_cmd_in_subprocess(['powershell.exe',
                               f'{SERVICE_CONST.NSSM_PATH} set {self.service_name} DisplayName {self.service_name}'],
                               logger=self.logger)
        self.logger.info(f'Done installing {self.service_name}')

    def start_service(self) :
        self.logger.info(f'Starting {self.service_name}...')
        #start the service using net
        cmd = f'net start {self.service_name}'
        run_cmd_in_subprocess(['powershell.exe',cmd],logger=self.logger)
        self.logger.info(f'Done starting {self.service_name}')

    def service_status(self) :
        #find or install NSSM in the current directory
        self.__find_install_NSSM()
        #get the service status
        cmd = f'{SERVICE_CONST.NSSM_PATH} status {self.service_name}'
        result = run_cmd_in_subprocess(['powershell.exe',cmd],logger=self.logger)
        self.logger.info(f'{self.service_name} status: {result.decode()}')

    def stop_service(self) :
        self.logger.info(f'Stopping {self.service_name}...')
        #stop the service using net
        cmd = f'net stop {self.service_name}'
        run_cmd_in_subprocess(['powershell.exe',cmd],logger=self.logger)
        self.logger.info(f'Done stopping {self.service_name}')

    def remove_service(self,remove_env_vars=False,remove_nssm=False) :
        self.logger.info(f'Removing {self.service_name}...')
        #find or install NSSM in the current directory
        self.__find_install_NSSM()
        #using NSSM
        cmd = f'{SERVICE_CONST.NSSM_PATH} remove {self.service_name} confirm'
        run_cmd_in_subprocess(['powershell.exe',cmd],logger=self.logger)
        self.logger.info('Service removed')
        #remove NSSM if requested
        if remove_nssm :
            if SERVICE_CONST.NSSM_PATH.is_file() :
                try :
                    run_cmd_in_subprocess(['powershell.exe',f'del {SERVICE_CONST.NSSM_PATH}'],logger=self.logger)
                except CalledProcessError :
                    msg = f'WARNING: failed to delete {SERVICE_CONST.NSSM_PATH}. '
                    msg+= 'You are free to delete it manually if you would like.'
                    self.logger.info(msg)
            else :
                msg = f'NSSM does not exist at {SERVICE_CONST.NSSM_PATH} so it will not be removed'
                self.logger.info(msg)
        else :
            if SERVICE_CONST.NSSM_PATH.is_file() :
                msg = f'NSSM executable at {SERVICE_CONST.NSSM_PATH} will be retained'
                self.logger.info(msg)
        super().remove_service(remove_env_vars=remove_env_vars)

    def _write_env_var_file(self) :
        code = ''
        for evn in self.env_var_names :
            val = os.path.expandvars(f'${evn}')
            if val==f'${evn}' :
                raise RuntimeError(f'ERROR: value not found for expected environment variable {evn}!')
            code += f'{evn}\n'
        if code=='' :
            return False
        with open(self.env_var_filepath,'w') as fp :
            fp.write(code)
        return True

    def __copy_libsodium_dll_to_system32(self) :
        """
        Ensure that the libsodium.dll file exists in C:\Windows\system32
        (Needed to properly load it when running as a service)
        """
        system32_path = pathlib.Path(r'C:\Windows\system32')/'libsodium.dll'
        if system32_path.is_file() :
            return
        current_env_dll = ctypes.util.find_library('libsodium')
        if current_env_dll is not None :
            shutil.copy(pathlib.Path(current_env_dll),system32_path)
        else :
            errmsg = f'ERROR: could not locate libsodium DLL to copy to system32 folder for {self.service_name}!'
            self.logger.error(errmsg,FileNotFoundError)

    def __find_install_NSSM(self,move_local=True) :
        """
        Ensure the NSSM executable exists in the expected location.
        If it exists in the current directory, move it to the expected location.
        If it doesn't exist anywhere, try to download it from the web, but that's finicky in powershell.
        """
        if SERVICE_CONST.NSSM_PATH.is_file() :
            return
        else :
            if (pathlib.Path()/SERVICE_CONST.NSSM_PATH.name).is_file() and move_local :
                (pathlib.Path()/SERVICE_CONST.NSSM_PATH.name).replace(SERVICE_CONST.NSSM_PATH)
                return self.__find_install_NSSM(move_local=False)
            SERVICE_CONST.LOGGER.info(f'Installing NSSM from {SERVICE_CONST.NSSM_DOWNLOAD_URL}...')
            nssm_zip_file_name = SERVICE_CONST.NSSM_DOWNLOAD_URL.split('/')[-1]
            run_cmd_in_subprocess(['powershell.exe',
                                   '[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12'],
                                   logger=self.logger)
            cmd_tuples = [
                (f'curl {SERVICE_CONST.NSSM_DOWNLOAD_URL} -O',
                f'Invoke-WebRequest -Uri {SERVICE_CONST.NSSM_DOWNLOAD_URL} -OutFile {nssm_zip_file_name}'),
                (f'tar -xf {pathlib.Path() / nssm_zip_file_name}',
                f'Expand-Archive {nssm_zip_file_name} -DestinationPath {pathlib.Path().resolve()}'),
                (f'del {nssm_zip_file_name}',
                f'Remove-Item -Path {nssm_zip_file_name}'),
                (f'move {pathlib.Path() / nssm_zip_file_name.rstrip(".zip") / "win64" / "nssm.exe"} {pathlib.Path()}',
                f'''Move-Item -Path {pathlib.Path()/nssm_zip_file_name.rstrip(".zip")/"win64"/"nssm.exe"} \
                    -Destination {SERVICE_CONST.NSSM_PATH}'''),
                (f'rmdir /S /Q {nssm_zip_file_name.rstrip(".zip")}',
                f'Remove-Item -Recurse -Force {nssm_zip_file_name.rstrip(".zip")}'),
            ]
            for cmd in cmd_tuples :
                try :
                    run_cmd_in_subprocess(['powershell.exe',cmd[1]],logger=self.logger)
                except CalledProcessError :
                    run_cmd_in_subprocess(cmd[0],shell=True,logger=self.logger)
            SERVICE_CONST.LOGGER.debug('Done installing NSSM')

################################################################################
################################ LINUX SERVICES ################################
################################################################################

class LinuxServiceManager(ServiceManagerBase) :
    """
    Class for working with Linux Services/daemons
    """

    @property
    def env_var_names(self):
        for evn in super().env_var_names :
            yield evn
        #get the names of environment variables from the env_var file
        if self.env_var_filepath.is_file() :
            with open(self.env_var_filepath,'r') as fp :
                lines = fp.readlines()
            for line in lines :
                try :
                    linesplit = (line.strip()).split('=')
                    if len(linesplit)==2 :
                        yield linesplit[0]
                except :
                    pass

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        self.daemon_working_dir_filepath = SERVICE_CONST.WORKING_DIR/f'{self.service_name}.service'
        self.daemon_filepath = SERVICE_CONST.DAEMON_SERVICE_DIR/self.daemon_working_dir_filepath.name

    def install_service(self) :
        super().install_service()
        #make sure systemd is running
        self.__check_systemd_installed()
        #write the daemon file pointing to the executable
        self.__write_daemon_file()
        #enable the service
        run_cmd_in_subprocess(['sudo','systemctl','daemon-reload'],logger=self.logger)
        run_cmd_in_subprocess(['sudo','systemctl','enable',f'{self.service_name}.service'],logger=self.logger)
        self.logger.info(f'Done installing {self.service_name}')

    def start_service(self) :
        self.logger.info(f'Starting {self.service_name}...')
        self.__check_systemd_installed()
        run_cmd_in_subprocess(['sudo','systemctl','daemon-reload'],logger=self.logger)
        run_cmd_in_subprocess(['sudo','systemctl','start',f'{self.service_name}.service'],logger=self.logger)
        self.logger.info(f'Done starting {self.service_name}')

    def service_status(self) :
        self.__check_systemd_installed()
        result = run_cmd_in_subprocess(['sudo','systemctl','status',f'{self.service_name}.service'],logger=self.logger)
        self.logger.info(f'{self.service_name} status: {result.decode()}')

    def stop_service(self) :
        self.logger.info(f'Stopping {self.service_name}...')
        self.__check_systemd_installed()
        run_cmd_in_subprocess(['sudo','systemctl','stop',f'{self.service_name}.service'],logger=self.logger)
        self.logger.info(f'Done stopping {self.service_name}')

    def remove_service(self,remove_env_vars=False,remove_nssm=False) :
        self.logger.info(f'Removing {self.service_name}...')
        self.__check_systemd_installed()
        run_cmd_in_subprocess(['sudo','systemctl','disable',f'{self.service_name}.service'],logger=self.logger)
        if self.daemon_filepath.exists() :
            run_cmd_in_subprocess(['sudo','rm','-f',str(self.daemon_filepath)],logger=self.logger)
        run_cmd_in_subprocess(['sudo','systemctl','daemon-reload'],logger=self.logger)
        run_cmd_in_subprocess(['sudo','systemctl','reset-failed'],logger=self.logger)
        self.logger.info('Service removed')
        if remove_nssm :
            warnmsg = "WARNING: requested to remove NSSM along with the Service, "
            warnmsg+= "but Linux Services don't install NSSM so nothing was done."
            self.logger.warning(warnmsg)
        super().remove_service(remove_env_vars=remove_env_vars)

    def _write_env_var_file(self) :
        code = ''
        for evn in self.env_var_names :
            val = os.path.expandvars(f'${evn}')
            if val==f'${evn}' :
                raise RuntimeError(f'ERROR: value not found for expected environment variable {evn}!')
            code += f'{evn}={val}\n'
        if code=='' :
            return False
        with open(self.env_var_filepath,'w') as fp :
            fp.write(code)
        run_cmd_in_subprocess(['chmod','go-rwx',self.env_var_filepath])
        return True

    def __check_systemd_installed(self) :
        """
        Raises an error if systemd is not installed (systemd is needed to control Linux daemons)
        """
        check = run_cmd_in_subprocess(['ps','--no-headers','-o','comm','1'],logger=self.logger)
        if check.decode().rstrip()!='systemd' :
            errmsg = 'ERROR: Installing programs as Services ("daemons") on Linux requires systemd!'
            errmsg = 'You can install systemd with "sudo apt install systemd" (or similar) and try again.'
            self.logger.error(errmsg,RuntimeError)

    def __write_daemon_file(self) :
        """
        Write the Unit/.service file to the daemon directory that calls the Python executable
        """
        #make sure the directory to hold the file exists
        if not SERVICE_CONST.DAEMON_SERVICE_DIR.is_dir() :
            SERVICE_CONST.LOGGER.info(f'Creating a new daemon service directory at {SERVICE_CONST.DAEMON_SERVICE_DIR}')
            SERVICE_CONST.DAEMON_SERVICE_DIR.mkdir(parents=True)
        #write out the file pointing to the python executable
        env_vars_needed = self._write_env_var_file()
        code = f'''\
            [Unit]
            Description = {self.service_dict['class'].__doc__.strip()}
            Requires = network-online.target remote-fs.target
            After = network-online.target remote-fs.target

            [Service]
            Type = simple
            User = {os.path.expandvars('$USER')}
            ExecStart = {sys.executable} {self.exec_fp}'''
        if env_vars_needed :
            code+=f'''\n\
            EnvironmentFile = {self.env_var_filepath}'''
        code+=f'''\n\
            WorkingDirectory = {pathlib.Path().resolve()}
            Restart = on-failure
            RestartSec = 30

            [Install]
            WantedBy = multi-user.target'''
        with open(self.daemon_working_dir_filepath,'w') as fp :
            fp.write(textwrap.dedent(code))
        run_cmd_in_subprocess(['sudo','mv',str(self.daemon_working_dir_filepath),str(self.daemon_filepath.parent)],
                              logger=self.logger)

################################################################################
######################## FILE-SCOPE VARIABLES/FUNCTIONS ########################
################################################################################

MANAGERS_BY_OS_NAME = {'Windows':WindowsServiceManager,
                       'Linux':LinuxServiceManager,}

def install() :
    #get the arguments
    parser = ServiceManagerBase.get_argument_parser('install')
    args = parser.parse_args()
    #run the tests if requested
    if args.service_class_name=='test' :
        test_python_code()
    else :
        if args.service_name is None :
            #default name of the Service is just the class name
            service_name = args.service_class_name
        else :
            service_name = args.service_name
        #make the list of arguments that should be sent to the run function in the executable (removing "service_name")
        argslist = sys.argv[2:]
        if '--service_name' in argslist :
            index = argslist.index('--service_name')
            argslist.pop(index)
            argslist.pop(index)
        #get the name of the OS and start the object
        operating_system = get_os_name()
        manager_args = [service_name]
        manager_kwargs = {'service_class_name':args.service_class_name,
                          'argslist':argslist,
                          'interactive':True,
                          'logger':SERVICE_CONST.LOGGER}
        manager_class = MANAGERS_BY_OS_NAME[operating_system]
        manager = manager_class(*manager_args,**manager_kwargs)
        #install the service
        manager.install_service()

def manage() :
    #get the arguments
    parser = ServiceManagerBase.get_argument_parser('manage')
    args = parser.parse_args()
    #get the name of the OS and start the object
    operating_system = get_os_name()
    manager_args = [args.service_name]
    manager_kwargs = {'interactive':True,
                      'logger':SERVICE_CONST.LOGGER}
    manager_class = MANAGERS_BY_OS_NAME[operating_system]
    manager = manager_class(*manager_args,**manager_kwargs)
    #run some function based on the run mode
    manager.run_manage_command(args.run_mode,remove_env_vars=args.remove_env_vars,remove_nssm=args.remove_nssm)

def main() :
    SERVICE_CONST.LOGGER.error('ERROR: please run "install" or "manage" instead of "main" for this file')

if __name__=='__main__' :
    main()