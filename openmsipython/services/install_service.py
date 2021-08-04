#imports
import sys, pathlib, os
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError
from ..utilities.argument_parsing import MyArgumentParser
from ..data_file_io.data_file_upload_directory import DataFileUploadDirectory
from ..pdv.lecroy_file_upload_directory import LecroyFileUploadDirectory

#################### HELPER FUNCTIONS ####################

#briefly test the python code of the Service to catch any errors
def test_python_code(config_file_path) :
    print('Testing code to check for errors...')
    print(f'Running all unittests in {UNITTEST_DIR_PATH}...')
    cmd = f'python -m unittest discover -s {UNITTEST_DIR_PATH} -v'
    p = Popen(cmd,stdout=PIPE,stderr=STDOUT,shell=True,universal_newlines=True,env=os.environ)
    for stdout_line in p.stdout :
        print(stdout_line,end='')
    return_code = p.wait()
    if return_code>0 :
        raise RuntimeError('ERROR: some unittest(s) failed! See output above for details.')
        return
    print('All unittest checks complete : )')
    return

#install the Service using NSSM
def install_service(service_name) :
    if config_file_path is None :
        raise RuntimeError('ERROR: installing the Service requires a config file, specified with the "--config" flag!')
    #set the environment variables needed to run in test and prod by default from user input
    #(other configs would need the user to work outside this script)
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
    #test the Python code to make sure the configs are all valid
    test_python_code(config_file_path)
    #find or install NSSM in the current directory
    find_install_NSSM()
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
    parser.add_subparsers(description=subp_desc,required=True)
    parser.add_subparser_arguments_from_class(DataFileUploadDirectory)
    parser.add_subparser_arguments_from_class(LecroyFileUploadDirectory)
    #parser arguments
    args = parser.parse_args()
    ##Add "Service" to the given name of the service
    #service_name = args.service_name+'Service'

if __name__=='__main__' :
    main()
