#imports
import sys, pathlib, os, textwrap
from subprocess import Popen, PIPE, STDOUT
from ..shared.argument_parsing import MyArgumentParser
from .config import SERVICE_CONST
from .utilities import get_os_name, set_env_var_from_user_input, find_install_NSSM
from .utilities import run_cmd_in_subprocess, copy_libsodium_dll_to_system32

#################### HELPER FUNCTIONS ####################

def set_env_vars(interactive=True) :
    """
    set the necessary environment variables
    """
    env_var_names_descs = [('KAFKA_TEST_CLUSTER_USERNAME','Kafka TESTING cluster username'),
                           ('KAFKA_TEST_CLUSTER_PASSWORD','Kafka TESTING cluster password'),
                           ('KAFKA_PROD_CLUSTER_USERNAME','Kafka PRODUCTION cluster username'),
                           ('KAFKA_PROD_CLUSTER_PASSWORD','Kafka PRODUCTION cluster password'),
                        ]
    variables_set = False
    for env_var_tuple in env_var_names_descs :
        if (not interactive) and (env_var_tuple[0] in ('KAFKA_PROD_CLUSTER_USERNAME','KAFKA_PROD_CLUSTER_PASSWORD')) :
            continue
        if os.path.expandvars(f'${env_var_tuple[0]}') == f'${env_var_tuple[0]}' :
            if interactive :
                set_env_var_from_user_input(*env_var_tuple)
                variables_set = True
            else :
                raise RuntimeError(f'ERROR: a value for the {env_var_tuple[1]} environment variable is not set!')
        else :
            if interactive :
                choice = input(f'A value for the {env_var_tuple[1]} is already set, would you like to reset it? [y/(n)]: ')
                if choice.lower() in ('yes','y') :
                    set_env_var_from_user_input(*env_var_tuple)
                    variables_set = True
    return variables_set

def test_python_code() :
    """
    briefly test the python code of the Service to catch any errors
    """
    must_rerun = set_env_vars()
    if must_rerun :
        msg = 'New values for environment variables have been set. '
        msg+= 'Please close this window and rerun InstallService so that their values get picked up.'
        SERVICE_CONST.LOGGER.info(msg)
        sys.exit(0)
    SERVICE_CONST.LOGGER.debug('Testing code to check for errors...')
    unittest_dir_path = pathlib.Path(__file__).parent.parent.parent / 'test' / 'unittests'
    SERVICE_CONST.LOGGER.debug(f'Running all unittests in {unittest_dir_path}...')
    cmd = f'python -m unittest discover -s {unittest_dir_path} -vf'
    p = Popen(cmd,stdout=PIPE,stderr=STDOUT,shell=True,universal_newlines=True,env=os.environ)
    for stdout_line in p.stdout :
        print(stdout_line,end='')
    return_code = p.wait()
    if return_code>0 :
        raise RuntimeError('ERROR: some unittest(s) failed! See output above for details.')
        return
    SERVICE_CONST.LOGGER.debug('All unittest checks complete : )')

def write_executable_file(service_dict,service_name,argslist,filepath=None) :
    """
    write out the executable python file that the service will actually be running
    """
    code = f'''\
        if __name__=='__main__' :
            try :
                from {service_dict['filepath']} import {service_dict['func_name']}
                {service_dict['func_name']}({argslist})
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
        exec_fp = filepath
    else :
        exec_fp = pathlib.Path(__file__).parent/'working_dir'
        exec_fp = exec_fp/f'{service_name}{SERVICE_CONST.SERVICE_EXECUTABLE_NAME_STEM}'
    with open(exec_fp,'w') as fp :
        fp.write(textwrap.dedent(code))
    return exec_fp

def write_daemon_file(service_dict,service_name,exec_filepath) :
    #make sure the directory to hold the file exists
    if not SERVICE_CONST.DAEMON_SERVICE_DIR.is_dir() :
        SERVICE_CONST.LOGGER.info(f'Creating a new daemon service directory at {SERVICE_CONST.DAEMON_SERVICE_DIR}')
        SERVICE_CONST.DAEMON_SERVICE_DIR.mkdir(parents=True)
    #write out the file pointing to the python executable
    code = f'''\
        [Unit]
        Description = {service_dict['class'].__doc__.strip()}
        Requires = network-online.target remote-fs.target
        After = network-online.target remote-fs.target

        [Service]
        Type = simple
        ExecStart = {sys.executable} {exec_filepath}
        User = {service_name}
        WorkingDirectory = {pathlib.Path().resolve()}
        Restart = on-failure
        RestartSec = 30

        [Install]
        WantedBy = multi-user.target'''
    daemon_working_dir_filepath = SERVICE_CONST.WORKING_DIR/f'{service_name}.service'
    with open(daemon_working_dir_filepath,'w') as fp :
        fp.write(textwrap.dedent(code))
    run_cmd_in_subprocess(['sudo','mv',str(daemon_working_dir_filepath),str(SERVICE_CONST.DAEMON_SERVICE_DIR)])

def install_service(service_class_name,service_name,argslist,operating_system,interactive=True) :
    """
    install the Service using NSSM
    """
    #set the environment variables
    must_rerun = set_env_vars(interactive=interactive)
    if must_rerun :
        msg = 'New values for environment variables have been set. '
        msg+= 'Please close this window and rerun InstallService so that their values get picked up.'
        SERVICE_CONST.LOGGER.info(msg)
        sys.exit(0)
    #find the dictionary with details about the program that will run
    service_dict = [sd for sd in SERVICE_CONST.AVAILABLE_SERVICES if sd['script_name']==service_class_name]
    if len(service_dict)!=1 :
        errmsg = f'ERROR: could not find the Service dictionary for {service_name} (a {service_class_name} program)! '
        errmsg+= f'service_dict = {service_dict}'
        raise RuntimeError(errmsg)
    service_dict = service_dict[0]
    #write out the executable file
    exec_filepath = write_executable_file(service_dict,service_name,argslist)
    #install the service
    msg='Installing a'
    if service_class_name[0].lower() in ('a','e','i','o','u','y') :
        msg+='n'
    msg+=f' program {service_class_name} as "{service_name}" from executable at {exec_filepath}...'
    SERVICE_CONST.LOGGER.info(msg)
    #on Windows, it's a Service managed using NSSM
    if operating_system=='Windows' :
        #if it doesn't exist there yet, copy the libsodium.dll file to C:\Windows\system32
        copy_libsodium_dll_to_system32()
        #find or install NSSM to run the executable
        find_install_NSSM()
        #run NSSM
        cmd = f'{SERVICE_CONST.NSSM_EXECUTABLE_PATH} install {service_name} \"{sys.executable}\" \"{exec_filepath}\"'
        run_cmd_in_subprocess(['powershell.exe',cmd])
        run_cmd_in_subprocess(['powershell.exe',
                                f'{SERVICE_CONST.NSSM_EXECUTABLE_PATH} set {service_name} DisplayName {service_name}'])
    #on Linux, it's a daemon managed using systemd
    elif operating_system=='Linux' :
        #make sure systemd is running
        check = run_cmd_in_subprocess(['ps','--no-headers','-o','comm','1'])
        if check.decode().rstrip()!='systemd' :
            errmsg = 'ERROR: Installing programs as Services ("daemons") on Linux requires systemd!'
            errmsg = 'You can install systemd with "sudo apt install systemd" (or similar) and try again.'
            SERVICE_CONST.LOGGER.error(errmsg,RuntimeError)
        #write the daemon file pointing to the executable
        write_daemon_file(service_dict,service_name,exec_filepath)
        #enable the service
        run_cmd_in_subprocess(['sudo','systemctl','daemon-reload'])
        run_cmd_in_subprocess(['sudo','systemctl','enable',f'{service_name}.service'])
    SERVICE_CONST.LOGGER.info(f'Done installing {service_name}')

#################### MAIN FUNCTION ####################

def main() :
    #get the arguments
    parser = MyArgumentParser()
    #subparsers from the classes that could be run
    subp_desc = 'The name of a runnable class to install as a service must be given as the first positional argument. '
    subp_desc = 'Adding one of these class names to the command line along with "-h" will show additional help.'
    parser.add_subparsers(description=subp_desc,required=True,dest='service_class_name')
    for service_dict in SERVICE_CONST.AVAILABLE_SERVICES :
        parser.add_subparser_arguments_from_class(service_dict['class'],addl_args=['optional_service_name'])
    #parser arguments
    args = parser.parse_args()
    #just run the test if requested
    if args.service_class_name=='test' :
        test_python_code()
    else :
        #Add "Service" to the name of the class that will run to get the default name of the Service
        if args.service_name is None :
            service_name = args.service_class_name+'Service'
        else :
            service_name = args.service_name
        #make the list of arguments that should be sent to the run function in the executable
        argslist = sys.argv[2:]
        #remove the "service_name" argument since that doesn't go to the executable
        if '--service_name' in argslist :
            index = argslist.index('--service_name')
            argslist.pop(index)
            argslist.pop(index)
        #get the name of the OS
        operating_system = get_os_name()
        #install the service
        install_service(args.service_class_name,service_name,argslist,operating_system)

if __name__=='__main__' :
    main()
