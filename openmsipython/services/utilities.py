#imports
import pathlib, os
from subprocess import check_output, CalledProcessError
from .config import SERVICE_CONST

def run_cmd_in_subprocess(args,*,shell=False) :
    """
    run a command in a subprocess and return its result, printing and re-throwing any exceptions it causes
    """
    if isinstance(args,str) :
        args = [args]
    try :
        result = check_output(args,shell=shell,env=os.environ)
        return result
    except CalledProcessError as e :
        SERVICE_CONST.LOGGER.error(f'ERROR: failed to run a command. output:\n{e.output.decode()}')
        raise e

def remove_machine_env_var(var_name) :
    """
    remove a machine environment variable using a powershell command given its name
    """
    pwrsh_cmd = f'[Environment]::SetEnvironmentVariable("{var_name}",$null,[EnvironmentVariableTarget]::Machine)'
    run_cmd_in_subprocess(['powershell.exe',pwrsh_cmd])

def set_machine_env_var(var_name,var_val) :
    """
    set a machine environment variable using a powershell command given its name and value
    """
    pwrsh_cmd = f'[Environment]::SetEnvironmentVariable("{var_name}","{var_val}",[EnvironmentVariableTarget]::Machine)'
    run_cmd_in_subprocess(['powershell.exe',pwrsh_cmd])
    os.environ[var_name]=var_val

def set_env_var_from_user_input(var_name,var_desc) :
    """
    set a machine environment variable with the given name and description based on user input
    """
    var_val = input(f'Please enter the {var_desc}: ')
    set_machine_env_var(var_name,var_val)

#if NSSM doesn't exist in the current directory, install it from the web
def find_install_NSSM() :
    if SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file() :
        return
    else :
        SERVICE_CONST.LOGGER.info(f'Installing NSSM from {SERVICE_CONST.NSSM_DOWNLOAD_URL}...')
        nssm_zip_file_name = SERVICE_CONST.NSSM_DOWNLOAD_URL.split('/')[-1]
        run_cmd_in_subprocess(['powershell.exe','[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12'])
        cmd_tuples = [
            (f'curl {SERVICE_CONST.NSSM_DOWNLOAD_URL} -O',
             f'Invoke-WebRequest -Uri {SERVICE_CONST.NSSM_DOWNLOAD_URL} -OutFile {nssm_zip_file_name}'),
            (f'tar -xf {pathlib.Path() / nssm_zip_file_name}',
             f'Expand-Archive {nssm_zip_file_name} -DestinationPath {pathlib.Path().resolve()}'),
            (f'del {nssm_zip_file_name}',
             f'Remove-Item -Path {nssm_zip_file_name}'),
            (f'move {pathlib.Path() / nssm_zip_file_name.rstrip(".zip") / "win64" / "nssm.exe"} {pathlib.Path()}',
             f'''Move-Item -Path {pathlib.Path()/nssm_zip_file_name.rstrip(".zip")/"win64"/"nssm.exe"} \
                 -Destination {SERVICE_CONST.NSSM_EXECUTABLE_PATH}'''),
            (f'rmdir /S /Q {nssm_zip_file_name.rstrip(".zip")}',
             f'Remove-Item -Recurse -Force {nssm_zip_file_name.rstrip(".zip")}'),
        ]
        for cmd in cmd_tuples :
            try :
                run_cmd_in_subprocess(['powershell.exe',cmd[1]])
            except CalledProcessError :
                run_cmd_in_subprocess(cmd[0],shell=True)
        SERVICE_CONST.LOGGER.debug('Done installing NSSM')