#imports
from subprocess import CalledProcessError
from ..shared.argument_parsing import MyArgumentParser
from .config import SERVICE_CONST
from .utilities import get_os_name, run_cmd_in_subprocess, remove_machine_env_var, find_install_NSSM

#################### HELPER FUNCTIONS ####################

def start_service(service_name,operating_system) :
    """
    start the Service
    """
    SERVICE_CONST.LOGGER.info(f'Starting {service_name}...')
    if operating_system=='Windows' :
        #start the service using net
        cmd = f'net start {service_name}'
        run_cmd_in_subprocess(['powershell.exe',cmd])
    elif operating_system=='Linux' :
        run_cmd_in_subprocess(['sudo','systemctl','daemon-reload'])
        run_cmd_in_subprocess(['sudo','systemctl','start',f'{service_name}.service'])
    SERVICE_CONST.LOGGER.info(f'Done starting {service_name}')

def service_status(service_name,operating_system) :
    """
    get the status of the service
    """
    if operating_system=='Windows' :
        #find or install NSSM in the current directory
        find_install_NSSM()
        #get the service status
        cmd = f'{SERVICE_CONST.NSSM_EXECUTABLE_PATH} status {service_name}'
        result = run_cmd_in_subprocess(['powershell.exe',cmd])
    elif operating_system=='Linux' :
        result = run_cmd_in_subprocess(['sudo','systemctl','status',f'{service_name}.service'])
    SERVICE_CONST.LOGGER.info(f'{service_name} status: {result.decode()}')

def stop_service(service_name,operating_system) :
    """
    stop the Service
    """
    SERVICE_CONST.LOGGER.info(f'Stopping {service_name}...')
    if operating_system=='Windows' :
        #stop the service using net
        cmd = f'net stop {service_name}'
        run_cmd_in_subprocess(['powershell.exe',cmd])
    elif operating_system=='Linux' :
        run_cmd_in_subprocess(['sudo','systemctl','stop',f'{service_name}.service'])
    SERVICE_CONST.LOGGER.info(f'Done stopping {service_name}')

def remove_service(service_name,operating_system,remove_env_vars=False,remove_nssm=False) :
    """
    remove the Service
    """
    #find or install NSSM in the current directory
    find_install_NSSM()
    #remove the service
    SERVICE_CONST.LOGGER.info(f'Removing {service_name}...')
    if operating_system=='Windows' :
        #using NSSM
        cmd = f'{SERVICE_CONST.NSSM_EXECUTABLE_PATH} remove {service_name} confirm'
        run_cmd_in_subprocess(['powershell.exe',cmd])
    elif operating_system=='Linux' :
        run_cmd_in_subprocess(['sudo','systemctl','disable',f'{service_name}.service'])
        daemon_filepath = SERVICE_CONST.DAEMON_SERVICE_DIR/f'{service_name}.service'
        if daemon_filepath.exists() :
            run_cmd_in_subprocess(['sudo','rm','-f',str(daemon_filepath)])
        run_cmd_in_subprocess(['sudo','systemctl','daemon-reload'])
        run_cmd_in_subprocess(['sudo','systemctl','reset-failed'])
    SERVICE_CONST.LOGGER.info('Service removed')
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
    #remove NSSM if requested
    if remove_nssm :
        if SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file() :
            try :
                run_cmd_in_subprocess(['powershell.exe',f'del {SERVICE_CONST.NSSM_EXECUTABLE_PATH}'])
            except CalledProcessError :
                msg = f'WARNING: failed to delete {SERVICE_CONST.NSSM_EXECUTABLE_PATH}. '
                msg+= 'You are free to delete it manually if you would like.'
                SERVICE_CONST.LOGGER.info(msg)
        else :
            msg = f'NSSM does not exist at {SERVICE_CONST.NSSM_EXECUTABLE_PATH} so it will not be removed'
            SERVICE_CONST.LOGGER.info(msg)
    else :
        if SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file() :
            msg = f'NSSM executable at {SERVICE_CONST.NSSM_EXECUTABLE_PATH} will be retained'
            SERVICE_CONST.LOGGER.info(msg)
    SERVICE_CONST.LOGGER.info(f'Done removing {service_name}')

#################### MAIN FUNCTION ####################

def main() :
    #get the arguments
    parser = MyArgumentParser()
    parser.add_arguments('service_name','run_mode','remove_env_vars','remove_nssm')
    args = parser.parse_args()
    #figure out the OS that we're running on
    operating_system = get_os_name()
    #run some of the helper functions above based on the run mode
    if args.run_mode in ['start'] :
        start_service(args.service_name,operating_system)
    if args.run_mode in ['status'] :
        service_status(args.service_name,operating_system)
    if args.run_mode in ['stop','stop_and_remove'] :
        stop_service(args.service_name,operating_system)
    if args.run_mode in ['remove','stop_and_remove'] :
        remove_service(args.service_name,operating_system,
                       remove_env_vars=args.remove_env_vars,remove_nssm=args.remove_nssm)

if __name__=='__main__' :
    main()
    
