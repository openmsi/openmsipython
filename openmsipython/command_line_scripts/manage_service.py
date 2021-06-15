#imports
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError
import sys, pathlib, os

#################### FILE-SCOPE CONSTANTS ####################

SERVICE_NAME = 'OpenMSIDirectoryStreamService'
SERVICE_DISPLAY_NAME = 'Open MSI Directory Stream Service'
SERVICE_DESCRIPTION = 'Automatically produce to a Kafka topic any files added to a watched directory'
NSSM_DOWNLOAD_URL = 'https://nssm.cc/release/nssm-2.24.zip'
PYTHON_CODE_PATH = pathlib.Path(__file__).parent.parent / 'services' / 'openmsi_directory_stream_service.py'
UNITTEST_DIR_PATH = (pathlib.Path(__file__).parent.parent.parent / 'test' / 'unittests').resolve()

#################### HELPER FUNCTIONS ####################

#run a command in a subprocess and return its result, printing and re-throwing any exceptions it causes
def run_cmd_in_subprocess(args,*,shell=False) :
    if isinstance(args,str) :
        args = [args]
    try :
        result = check_output(args,shell=shell,env=os.environ)
        return result
    except CalledProcessError as e :
        print(f'ERROR: failed to run a command. output:\n{e.output.decode}')
        raise e

#remove a machine environment variable using a powershell command given its name
def remove_machine_env_var(var_name) :
    pwrsh_cmd = f'[Environment]::SetEnvironmentVariable("{var_name}",$null,[EnvironmentVariableTarget]::Machine)'
    run_cmd_in_subprocess(['powershell.exe',pwrsh_cmd])

#set a machine environment variable using a powershell command given its name and value
def set_machine_env_var(var_name,var_val) :
    pwrsh_cmd = f'[Environment]::SetEnvironmentVariable("{var_name}","{var_val}",[EnvironmentVariableTarget]::Machine)'
    run_cmd_in_subprocess(['powershell.exe',pwrsh_cmd])
    os.environ[var_name]=var_val

#set a machine environment variable with the given name and description based on user input
def set_env_var_from_user_input(var_name,var_desc) :
    var_val = input(f'Please enter the {var_desc}: ')
    set_machine_env_var(var_name,var_val)

#briefly test the python code of the Service to catch any errors
def test_python_code(config_file_path) :
    print('Testing Service code to check for errors...')
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

#if NSSM doesn't exist in the current directory, install it from the web
def find_install_NSSM() :
    if 'nssm.exe' in check_output('dir',shell=True).decode() :
        return
    else :
        print(f'Installing NSSM from {NSSM_DOWNLOAD_URL}...')
        nssm_zip_file_name = NSSM_DOWNLOAD_URL.split('/')[-1]
        cmd_tuples = [
            (f'curl {NSSM_DOWNLOAD_URL} -O',f'Invoke-WebRequest -Uri {NSSM_DOWNLOAD_URL} -OutFile {nssm_zip_file_name}'),
            (f'tar -xf {pathlib.Path() / nssm_zip_file_name}',f'Expand-Archive {nssm_zip_file_name} -DestinationPath {pathlib.Path().resolve()}'),
            (f'del {nssm_zip_file_name}',f'Remove-Item -Path {nssm_zip_file_name}'),
            (f'move {pathlib.Path() / nssm_zip_file_name.rstrip(".zip") / "win64" / "nssm.exe"} {pathlib.Path()}',
                f'Move-Item -Path {pathlib.Path()/nssm_zip_file_name.rstrip(".zip")/"win64"/"nssm.exe"} -Destination {(pathlib.Path()/"nssm.exe").resolve()}'),
            (f'rmdir /S /Q {nssm_zip_file_name.rstrip(".zip")}',f'Remove-Item -Recurse -Force {nssm_zip_file_name.rstrip(".zip")}'),
        ]
        for cmd in cmd_tuples :
            try :
                run_cmd_in_subprocess(['powershell.exe',cmd[1]])
            except CalledProcessError :
                run_cmd_in_subprocess(cmd[0],shell=True)
                
        print('Done.')

#install the Service using NSSM
def install_service(config_file_path) :
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
    print(f'Installing {SERVICE_NAME}...')
    cmd = f'.\\nssm.exe install \"{SERVICE_NAME}\" \"{sys.executable}\" \"{PYTHON_CODE_PATH} {pathlib.Path(config_file_path).resolve()}\"'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    run_cmd_in_subprocess(['powershell.exe',f'.\\nssm.exe set {SERVICE_NAME} DisplayName {SERVICE_DISPLAY_NAME}'])
    run_cmd_in_subprocess(['powershell.exe',f'.\\nssm.exe set {SERVICE_NAME} Description {SERVICE_DESCRIPTION}'])
    print('Done')

#start the Service
def start_service() :
    #start the service using net
    print(f'Starting {SERVICE_NAME}...')
    cmd = f'net start {SERVICE_NAME}'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    print('Done')

#use NSSM to get the status of the service
def service_status() :
    #find or install NSSM in the current directory
    find_install_NSSM()
    #get the service status
    cmd = f'.\\nssm.exe status {SERVICE_NAME}'
    result = run_cmd_in_subprocess(['powershell.exe',cmd])
    print(result.decode())

#stop the Service
def stop_service() :
    #stop the service using net
    print(f'Stopping {SERVICE_NAME}...')
    cmd = f'net stop {SERVICE_NAME}'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    print('Done')

#remove the Service
def remove_service() :
    #find or install NSSM in the current directory
    find_install_NSSM()
    #remove the service using NSSM
    print(f'Removing {SERVICE_NAME}...')
    cmd = f'.\\nssm.exe remove {SERVICE_NAME} confirm'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    print('Service successfully removed')
    #remove the environment variables that were set when the service was installed
    try :
        remove_machine_env_var('KAFKA_TEST_CLUSTER_USERNAME')
        remove_machine_env_var('KAFKA_TEST_CLUSTER_PASSWORD')
        remove_machine_env_var('KAFKA_PROD_CLUSTER_USERNAME')
        remove_machine_env_var('KAFKA_PROD_CLUSTER_PASSWORD')
        print('Username/password environment variables successfully removed')
    except CalledProcessError :
        warnmsg = 'WARNING: failed to remove environment variables. '
        warnmsg+= 'You should remove any username/password environment variables manually even though the service is uninstalled!'
        print(warnmsg)
    #remove NSSM from the current directory
    if 'nssm.exe' in check_output('dir',shell=True).decode() :
        try :
            run_cmd_in_subprocess(['powershell.exe','del nssm.exe'])
        except CalledProcessError :
            print('WARNING: failed to delete nssm.exe in the current directory. You are free to delete it manually if you would like.')
    print('Done')

#################### MAIN FUNCTION ####################

def main() :
    #get the arguments
    parser = ArgumentParser()
    #first positional argument: run mode
    parser.add_argument('run_mode', choices=['install_and_start','install','start','status','stop','remove','stop_and_remove'])
    #optional arguments
    parser.add_argument('--config', help='Path to the config file to use in setting up the Service')
    args = parser.parse_args()
    #run some of the helper functions above based on the run mode
    if args.run_mode in ['install','install_and_start'] :
        install_service(args.config)
    if args.run_mode in ['start','install_and_start'] :
        start_service()
    if args.run_mode in ['status'] :
        service_status()
    if args.run_mode in ['stop','stop_and_remove'] :
        stop_service()
    if args.run_mode in ['remove','stop_and_remove'] :
        remove_service()

#run the main function, giving the run command and the config file path from the command line
if __name__=='__main__' :
    main()
