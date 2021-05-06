#imports
from argparse import ArgumentParser
from subprocess import Popen, PIPE, check_output
import sys, pathlib

#################### FILE-SCOPE CONSTANTS ####################

SERVICE_NAME = 'OpenMSIDirectoryStreamService'
SERVICE_DISPLAY_NAME = 'Open MSI Directory Stream Service'
SERVICE_DESCRIPTION = 'Automatically produce to a Kafka topic any files added to a watched directory'
NSSM_DOWNLOAD_URL = 'https://nssm.cc/release/nssm-2.24.zip'
PYTHON_CODE_PATH = pathlib.Path(__file__).parent.parent / 'services' / 'openmsi_directory_stream_service.py'

#################### HELPER FUNCTIONS ####################

#briefly test the python code of the Service to catch any errors
def test_python_code(config_file_path) :
    print('Testing Service code to check for errors...')
    p = Popen([sys.executable,str(PYTHON_CODE_PATH),config_file_path],stdout=PIPE,stdin=PIPE,stderr=PIPE)
    #see if running the python code produced any errors
    stdout,stderr = p.communicate(input='quit'.encode())
    if stderr.decode()!='' :
        raise RuntimeError(f'ERROR: something went wrong in testing the code with the current configuration. This is the error:\n{result[1].decode()}')
    print('Done testing code.')
    return

#if NSSM doesn't exist in the current directory, install it from the web
def find_install_NSSM() :
    if 'nssm.exe' in check_output('dir',shell=True).decode() :
        return
    else :
        print(f'Installing NSSM from {NSSM_DOWNLOAD_URL}...')
        result = check_output(f'curl {NSSM_DOWNLOAD_URL} -O',shell=True)
        nssm_zip_file_name = NSSM_DOWNLOAD_URL.split('/')[-1]
        result = check_output(f'tar -xf {pathlib.Path() / nssm_zip_file_name}',shell=True)
        result = check_output(f'move {pathlib.Path() / nssm_zip_file_name.rstrip(".zip") / "win64" / "nssm.exe"} {pathlib.Path()}',shell=True)
        result = check_output(f'del {nssm_zip_file_name}',shell=True)
        result = check_output(f'rmdir /S /Q {nssm_zip_file_name.rstrip(".zip")}',shell=True)
        result = result #pyflakes
        print('Done.')
        return
    return

#install the Service using NSSM
def install_service(config_file_path) :
    if config_file_path is None :
        raise RuntimeError('ERROR: installing the Service requires a config file, specified with the "--config" flag!')
    #test the Python code to make sure the configs are all valid
    test_python_code(config_file_path)
    #find or install NSSM in the current directory
    find_install_NSSM()
    #install the service using NSSM
    print(f'Installing {SERVICE_NAME}...')
    cmd = f'.\\nssm.exe install \"{SERVICE_NAME}\" \"{sys.executable}\" \"{PYTHON_CODE_PATH} {pathlib.Path(config_file_path).absolute()}\"'
    result = check_output(cmd,shell=True)
    result = check_output(f'.\\nssm.exe set {SERVICE_NAME} DisplayName {SERVICE_DISPLAY_NAME}')
    result = check_output(f'.\\nssm.exe set {SERVICE_NAME} Description {SERVICE_DESCRIPTION}')
    result = result #pyflakes
    print('Done')
    return

#start the Service
def start_service() :
    #start the service using net
    print(f'Starting {SERVICE_NAME}...')
    cmd = f'net start {SERVICE_NAME}'
    result = check_output(cmd,shell=True)
    result = result #pyflakes
    print('Done')
    return

#use NSSM to get the status of the service
def service_status() :
    #find or install NSSM in the current directory
    find_install_NSSM()
    #get the service status
    cmd = f'.\\nssm.exe status {SERVICE_NAME}'
    result = check_output(cmd,shell=True)
    print(result.decode())
    return

#stop the Service
def stop_service() :
    #stop the service using net
    print(f'Stopping {SERVICE_NAME}...')
    cmd = f'net stop {SERVICE_NAME}'
    result = check_output(cmd,shell=True)
    result = result #pyflakes
    print('Done')
    return
    pass

#remove the Service
def remove_service() :
    #find or install NSSM in the current directory
    find_install_NSSM()
    #remove the service using NSSM
    print(f'Removing {SERVICE_NAME}...')
    cmd = f'.\\nssm.exe remove {SERVICE_NAME} confirm'
    result = check_output(cmd,shell=True)
    result = result #pyflakes
    print('Done')
    return

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