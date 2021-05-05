#imports
from ..utilities.argument_parsing import config_path
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT, check_output
import sys, pathlib

#################### FILE-SCOPE CONSTANTS ####################

SERVICE_NAME = 'OpenMSIDirectoryStreamService'
SERVICE_DISPLAY_NAME = 'OpenMSI Directory Stream Service'
SERVICE_DESCRIPTION = 'Automatically produce to a Kafka topic any files added to a watched directory'

#################### HELPER FUNCTIONS ####################

#briefly test the python code of the Service to catch any errors
def test_python_code(config_file_path) :
    print('Testing Service code to check for errors (will take about 15 seconds)....')
    path_to_python_code = pathlib.Path(__file__).parent.parent / 'services' / 'openmsi_directory_stream_service.py'
    p = Popen([sys.executable,path_to_python_code,config_file_path],stdout=PIPE,stdin=PIPE,stderr=PIPE)
    #see if running the python code produced any errors
    result = p.communicate(timeout=10)
    if result[1].decode()!='' :
        raise RuntimeError(f'ERROR: something went wrong in testing the code with the current configuration. This is the error:\n{result[1].decode()}')
    #if no errors were thrown, try to give the "quit" command to the process
    result = p.communicate(input='quit')
    if result[1].decode()!='' :
        raise RuntimeError(f'ERROR: something went wrong in testing the code with the current configuration. This is the error:\n{result[1].decode()}')
    return

#if NSSM doesn't exist in the current directory, install it from the web
def find_install_NSSM() :
    pass

#install the Service using NSSM
def install_service(config_file_path) :
    if config_file_path is None :
        raise RuntimeError('ERROR: installing the Service requires a config file, specified with the "--config" flag!')
    #test the Python code to make sure the configs are all valid
    test_python_code(config_file_path)
    #find or install NSSM in the current directory
    find_install_NSSM()
    #install the service using NSSM
    pass

#start the Service
def start_service() :
    pass

#stop the Service
def stop_service() :
    pass

#remove the Service
def remove_service() :
    pass

#################### MAIN FUNCTION ####################

def main() :
    #get the arguments
    parser = ArgumentParser()
    #first positional argument: run mode
    parser.add_argument('run_mode', choices=['install_and_start','install','start','stop','remove','stop_and_remove'])
    #optional arguments
    parser.add_argument('--config', help=f'Path to the config file to use in setting up the Service')
    args = parser.parse_args()
    #run some of the helper functions above based on the run mode
    if args.run_mode in ['install','install_and_start'] :
        install_service(args.config)
    if args.run_mode in ['start','install_and_start'] :
        start_service()
    if args.run_mode in ['stop','stop_and_remove'] :
        stop_service()
    if args.run_mode in ['remove','stop_and_remove'] :
        remove_service()

#run the main function, giving the run command and the config file path from the command line
if __name__=='__main__' :
    main()