#imports
import sys, pathlib, os
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError
from ..utilities.argument_parsing import MyArgumentParser
from ..data_file_io.data_file_upload_directory import DataFileUploadDirectory
from ..pdv.lecroy_file_upload_directory import LecroyFileUploadDirectory

#################### HELPER FUNCTIONS ####################

#start the Service
def start_service(service_name) :
    #start the service using net
    print(f'Starting {service_name}...')
    cmd = f'net start {service_name}'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    print('Done')

#use NSSM to get the status of the service
def service_status(service_name) :
    #find or install NSSM in the current directory
    find_install_NSSM()
    #get the service status
    cmd = f'.\\nssm.exe status {service_name}'
    result = run_cmd_in_subprocess(['powershell.exe',cmd])
    print(result.decode())

#stop the Service
def stop_service(service_name) :
    #stop the service using net
    print(f'Stopping {service_name}...')
    cmd = f'net stop {service_name}'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    print('Done')

#remove the Service
def remove_service(service_name) :
    #find or install NSSM in the current directory
    find_install_NSSM()
    #remove the service using NSSM
    print(f'Removing {service_name}...')
    cmd = f'.\\nssm.exe remove {service_name} confirm'
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
    parser = MyArgumentParser(add_help=False)
    parser.add_arguments('service_name','run_mode')#parser arguments
    args = parser.parse_args()
    ##Add "Service" to the given name of the service
    #service_name = args.service_name+'Service'
    ##run some of the helper functions above based on the run mode
    #if args.run_mode in ['install','install_and_start'] :
    #    #set the python code that will be run based on the service name
    #    mainfunc = MAINS_BY_NAME[args.service_name]
    #    install_service(service_name)
    #if args.run_mode in ['start','install_and_start'] :
    #    start_service(service_name)
    #if args.run_mode in ['status'] :
    #    service_status(service_name)
    #if args.run_mode in ['stop','stop_and_remove'] :
    #    stop_service(service_name)
    #if args.run_mode in ['remove','stop_and_remove'] :
    #    remove_service(service_name)

if __name__=='__main__' :
    main()
    
