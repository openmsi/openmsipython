#imports
import pathlib, os, shutil, ctypes.util, platform
from subprocess import check_output, CalledProcessError
from .config import SERVICE_CONST

def get_os_name() :
    """
    Return the name of the operating system the Service is being installed or running on
    """
    if platform.system()=='Windows' :
        return 'Windows'
    elif platform.system()=='Linux' :
        return 'Linux'
    #MacOS is not supported
    elif platform.system()=='Darwin' :
        errmsg = 'ERROR: Installing programs as Services is not supported on MacOS!'
        SERVICE_CONST.LOGGER.error(errmsg,NotImplementedError)
    #otherwise I don't know what happened
    else :
        errmsg = f'ERROR: could not determine operating system from platform.system() output "{platform.system()}"'
        SERVICE_CONST.LOGGER.error(errmsg,ValueError)

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
        errmsg = 'ERROR: failed to run a command! '
        if e.output is not None and e.output.strip()!='' :
            errmsg+= f'\noutput:\n{e.output.decode()}'
        if e.stdout is not None and e.stdout.strip()!=''  :
            errmsg+= f'\nstdout:\n{e.stdout.decode()}'
        if e.stderr is not None and e.stderr.strip()!='' :
            errmsg+= f'\nstderr:\n{e.stderr.decode()}'
        SERVICE_CONST.LOGGER.error(errmsg,exc_obj=e)

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

def find_install_NSSM(move_local=True) :
    """
    Ensure the NSSM executable exists in the expected location.
    If it exists in the current directory, move it to the expected location.
    If it doesn't exist anywhere, try to download it from the web, but that's finicky in powershell.
    """
    if SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file() :
        return
    else :
        if (pathlib.Path()/SERVICE_CONST.NSSM_EXECUTABLE_PATH.name).is_file() and move_local :
            (pathlib.Path()/SERVICE_CONST.NSSM_EXECUTABLE_PATH.name).replace(SERVICE_CONST.NSSM_EXECUTABLE_PATH)
            return find_install_NSSM(move_local=False)
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

def copy_libsodium_dll_to_system32() :
    """
    Ensure that the libsodium.dll file exists in C:\Windows\system32
    (Needed to properly load it when running as a service)
    """
    system32_path = pathlib.Path(r'C:\Windows\system32')/'libsodium.dll'
    if system32_path.is_file() :
        return
    current_env_dll = ctypes.util.find_library('libsodium')
    if current_env_dll is not None :
        shutil.copy(pathlib.Path(current_env_dll),system32_path)
    else :
        raise ValueError('ERROR: could not locate libsodium DLL to copy to system32 folder for Service!')
