#imports
import sys, pathlib, os
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError
from ..utilities.argument_parsing import MyArgumentParser
from ..data_file_io.data_file_upload_directory import DataFileUploadDirectory
from ..pdv.lecroy_file_upload_directory import LecroyFileUploadDirectory
from .config import SERVICE_CONST

#################### HELPER FUNCTIONS ####################

#set the necessary environment variables
def set_env_vars() :
    env_var_names_descs = [('KAFKA_TEST_CLUSTER_USERNAME','Kafka TESTING cluster username'),
                           ('KAFKA_TEST_CLUSTER_PASSWORD','Kafka TESTING cluster password'),
                           ('KAFKA_PROD_CLUSTER_USERNAME','Kafka PRODUCTION cluster username'),
                           ('KAFKA_PROD_CLUSTER_PASSWORD','Kafka PRODUCTION cluster password'),
                        ]
    for env_var_tuple in env_var_names_descs :
        if os.path.expandvars(f'${env_var_tuple[0]}') == f'${env_var_tuple[0]}' :
            set_env_var_from_user_input(*env_var_tuple)
        else :
            choice = input(f'A value for the {env_var_tuple[1]} is already set, would you like to reset it? [y/(n)]: ')
            if choice.lower() in ('yes','y') :
                set_env_var_from_user_input(*env_var_tuple)

#briefly test the python code of the Service to catch any errors
def test_python_code() :
    print('Testing code to check for errors...')
    unittest_dir_path = pathlib.Path(__file__.parent.parent.parent) / 'test' / 'unittests'
    print(f'Running all unittests in {unittest_dir_path}...')
    cmd = f'python -m unittest discover -s {unittest_dir_path} -v'
    p = Popen(cmd,stdout=PIPE,stderr=STDOUT,shell=True,universal_newlines=True,env=os.environ)
    for stdout_line in p.stdout :
        print(stdout_line,end='')
    return_code = p.wait()
    if return_code>0 :
        raise RuntimeError('ERROR: some unittest(s) failed! See output above for details.')
        return
    print('All unittest checks complete : )')

#write out the executable python file that the service will actually be running
def write_executable_file(service_name,argslist) :
    pass

#install the Service using NSSM
def install_service(service_name,argslist) :
    ##set the environment variables
    #set_env_vars()
    ##test the Python code to make sure the configs are all valid
    #test_python_code()
    ##find or install NSSM in the current directory
    #find_install_NSSM()
    #write out the executable file
    write_executable_file(service_name,argslist)
    #install the service using NSSM
    print(f'Installing {service_name}...')
    cmd = f'.\\nssm.exe install \"{service_name}\" \"{sys.executable}\" \"{PYTHON_CODE_PATH} '
    cmd+= f'{pathlib.Path(config_file_path).resolve()}\"'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    run_cmd_in_subprocess(['powershell.exe',f'.\\nssm.exe set {service_name} DisplayName {SERVICE_DISPLAY_NAME}'])
    run_cmd_in_subprocess(['powershell.exe',f'.\\nssm.exe set {service_name} Description {SERVICE_DESCRIPTION}'])
    print('Done')

#################### MAIN FUNCTION ####################

def main() :
    #get the arguments
    parser = MyArgumentParser()
    #subparsers from the classes that could be run
    subp_desc = 'The name of a runnable class to install as a service must be given as the first positional argument. '
    subp_desc = 'Adding one of these class names to the command line along with "-h" will show additional help.'
    parser.add_subparsers(description=subp_desc,required=True,dest='service_name')
    parser.add_subparser_arguments_from_class(DataFileUploadDirectory)
    parser.add_subparser_arguments_from_class(LecroyFileUploadDirectory)
    #parser arguments
    args = parser.parse_args()
    print(SERVICE_CONST.AVAILABLE_SERVICES)
    ##Add "Service" to the given name of the service
    #service_name = args.service_name+'Service'
    ##install the service
    #install_service(service_name,sys.argv[2:])

if __name__=='__main__' :
    main()
