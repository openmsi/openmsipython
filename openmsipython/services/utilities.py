#imports
import sys, pathlib, os
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError
from ..utilities.argument_parsing import MyArgumentParser
from ..data_file_io.data_file_upload_directory import DataFileUploadDirectory
from ..pdv.lecroy_file_upload_directory import LecroyFileUploadDirectory
from .config import SERVICES_CONST

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
        print(f'ERROR: failed to run a command. output:\n{e.output.decode}')
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