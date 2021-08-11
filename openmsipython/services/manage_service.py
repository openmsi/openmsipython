#imports
from subprocess import CalledProcessError
from ..utilities.argument_parsing import MyArgumentParser
from .config import SERVICE_CONST
from .utilities import run_cmd_in_subprocess, remove_machine_env_var, find_install_NSSM

#################### HELPER FUNCTIONS ####################

def start_service(service_name) :
    """
    start the Service
    """
    #start the service using net
    SERVICE_CONST.LOGGER.info(f'Starting {service_name}...')
    cmd = f'net start {service_name}'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    SERVICE_CONST.LOGGER.info(f'Done starting {service_name}')

def service_status(service_name) :
    """
    use NSSM to get the status of the service
    """
    #find or install NSSM in the current directory
    find_install_NSSM()
    #get the service status
    cmd = f'{SERVICE_CONST.NSSM_EXECUTABLE_PATH} status {service_name}'
    result = run_cmd_in_subprocess(['powershell.exe',cmd])
    SERVICE_CONST.LOGGER.info(f'{service_name} status: {result.decode()}')

def stop_service(service_name) :
    """
    stop the Service
    """
    #stop the service using net
    SERVICE_CONST.LOGGER.info(f'Stopping {service_name}...')
    cmd = f'net stop {service_name}'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    SERVICE_CONST.LOGGER.info(f'Done stopping {service_name}')

def remove_service(service_name,remove_env_vars) :
    """
    remove the Service
    """
    #find or install NSSM in the current directory
    find_install_NSSM()
    #remove the service using NSSM
    SERVICE_CONST.LOGGER.info(f'Removing {service_name}...')
    cmd = f'{SERVICE_CONST.NSSM_EXECUTABLE_PATH} remove {service_name} confirm'
    run_cmd_in_subprocess(['powershell.exe',cmd])
    SERVICE_CONST.LOGGER.info('Service successfully removed')
    #remove the environment variables that were set when the service was installed
    if remove_env_vars :
        try :
            remove_machine_env_var('KAFKA_TEST_CLUSTER_USERNAME')
            remove_machine_env_var('KAFKA_TEST_CLUSTER_PASSWORD')
            remove_machine_env_var('KAFKA_PROD_CLUSTER_USERNAME')
            remove_machine_env_var('KAFKA_PROD_CLUSTER_PASSWORD')
            SERVICE_CONST.LOGGER.info('Username/password environment variables successfully removed')
        except CalledProcessError :
            warnmsg = 'WARNING: failed to remove environment variables. You should remove any username/password '
            warnmsg+= 'environment variables manually even though the service is uninstalled!'
            SERVICE_CONST.LOGGER.info(warnmsg)
    else :
        SERVICE_CONST.LOGGER.info('Environment variables will be retained')
    ##remove NSSM from the working directory
    #if SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file() :
    #    try :
    #        run_cmd_in_subprocess(['powershell.exe',f'del {SERVICE_CONST.NSSM_EXECUTABLE_PATH}'])
    #    except CalledProcessError :
    #        msg = f'WARNING: failed to delete {SERVICE_CONST.NSSM_EXECUTABLE_PATH}. '
    #        msg+= 'You are free to delete it manually if you would like.'
    #        SERVICE_CONST.LOGGER.info()
    SERVICE_CONST.LOGGER.info(f'Done removing {service_name}')

#################### MAIN FUNCTION ####################

def main() :
    #get the arguments
    parser = MyArgumentParser()
    parser.add_arguments('service_name','run_mode','remove_env_vars')
    args = parser.parse_args()
    #Add "Service" to the given name of the service
    service_name = args.service_name+'Service'
    #run some of the helper functions above based on the run mode
    if args.run_mode in ['start'] :
        start_service(service_name)
    if args.run_mode in ['status'] :
        service_status(service_name)
    if args.run_mode in ['stop','stop_and_remove'] :
        stop_service(service_name)
    if args.run_mode in ['remove','stop_and_remove'] :
        remove_service(service_name,args.remove_env_vars)

if __name__=='__main__' :
    main()
    
