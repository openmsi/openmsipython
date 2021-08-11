#imports
import sys, pathlib, os, textwrap
from subprocess import Popen, PIPE, STDOUT
from ..utilities.argument_parsing import MyArgumentParser
from .config import SERVICE_CONST
from .utilities import set_env_var_from_user_input, find_install_NSSM, run_cmd_in_subprocess

#################### HELPER FUNCTIONS ####################

def set_env_vars() :
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
        if os.path.expandvars(f'${env_var_tuple[0]}') == f'${env_var_tuple[0]}' :
            set_env_var_from_user_input(*env_var_tuple)
            variables_set = True
        else :
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

def write_executable_file(service_name,argslist) :
    """
    write out the executable python file that the service will actually be running
    """
    service_dict = [sd for sd in SERVICE_CONST.AVAILABLE_SERVICES if sd['script_name']==service_name.rstrip('Service')]
    if len(service_dict)!=1 :
        errmsg = f'ERROR: could not find the Service dictionary for {service_name}! service_dict = {service_dict}'
        raise RuntimeError(errmsg)
    service_dict = service_dict[0]
    code = f'''\
        from {service_dict['filepath']} import {service_dict['func_name']}

        if __name__=='__main__' :
            {service_dict['func_name']}({argslist})

    '''
    exec_fp = pathlib.Path(__file__).parent/'working_dir'/f'{service_name}{SERVICE_CONST.SERVICE_EXECUTABLE_NAME_STEM}'
    with open(exec_fp,'w') as fp :
        fp.write(textwrap.dedent(code))
    return exec_fp

def install_service(service_name,argslist) :
    """
    install the Service using NSSM
    """
    #set the environment variables
    must_rerun = set_env_vars()
    if must_rerun :
        msg = 'New values for environment variables have been set. '
        msg+= 'Please close this window and rerun InstallService so that their values get picked up.'
        SERVICE_CONST.LOGGER.info(msg)
        sys.exit(0)
    #find or install NSSM in the current directory
    find_install_NSSM()
    #write out the executable file
    exec_filepath = write_executable_file(service_name,argslist)
    #install the service using NSSM
    SERVICE_CONST.LOGGER.info(f'Installing {service_name} from executable at {exec_filepath}...')
    cmd = f'{SERVICE_CONST.NSSM_EXECUTABLE_PATH} install {service_name} \"{sys.executable}\" \"{exec_filepath}\"'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    run_cmd_in_subprocess(['powershell.exe',
                           f'{SERVICE_CONST.NSSM_EXECUTABLE_PATH} set {service_name} DisplayName {service_name}'])
    SERVICE_CONST.LOGGER.info(f'Done installing {service_name}')

#################### MAIN FUNCTION ####################

def main() :
    #get the arguments
    parser = MyArgumentParser()
    #subparsers from the classes that could be run
    subp_desc = 'The name of a runnable class to install as a service must be given as the first positional argument. '
    subp_desc = 'Adding one of these class names to the command line along with "-h" will show additional help.'
    parser.add_subparsers(description=subp_desc,required=True,dest='service_name')
    for service_dict in SERVICE_CONST.AVAILABLE_SERVICES :
        parser.add_subparser_arguments_from_class(service_dict['class'])
    testparser = parser.add_subparser('test')
    #parser arguments
    args = parser.parse_args()
    #just run the test if requested
    if args.service_name=='test' :
        test_python_code()
    else :
        #Add "Service" to the given name of the service
        service_name = args.service_name+'Service'
        #install the service
        install_service(service_name,sys.argv[2:])

if __name__=='__main__' :
    main()
