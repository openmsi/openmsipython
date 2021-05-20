#imports
import subprocess, pathlib

#constants
TOP_DIR_PATH = (pathlib.Path(__file__).parent.parent).resolve()
UNITTEST_DIR_PATH = (pathlib.Path(__file__).parent / 'unittests').resolve()
TEST_REPO_STATUS_SCRIPT_PATH = (pathlib.Path(__file__).parent / 'test_repo_status.sh').resolve()
CWD = pathlib.Path().resolve()

def main() :
    #test pyflakes
    print('testing code consistency with pyflakes...')
    p = subprocess.Popen(f'cd {TOP_DIR_PATH}; pyflakes .; cd {CWD}; exit 0',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,universal_newlines=True)
    stdout,stderr = p.communicate()
    if stdout!='' :
        raise RuntimeError(f'ERROR: pyflakes check failed with output:\n{stdout}')
    print('Passed pyflakes check : )')
    #perform all the unittests
    print(f'Running all unittests in {UNITTEST_DIR_PATH}...')
    p = subprocess.Popen(f'python -m unittest discover -s {UNITTEST_DIR_PATH} -v',
                         stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True,universal_newlines=True)
    for stdout_line in p.stdout :
        print(stdout_line,end='')
    return_code = p.wait()
    if return_code>0 :
        print('ERROR: some unittest(s) failed! See output above for details.')
        return
    print('All unittest checks complete : )')
    #make sure the Github repo is still clean from its initial state
    print('Checking the status of the Git repo....')
    p = subprocess.Popen(f'cd {TOP_DIR_PATH}; sh {TEST_REPO_STATUS_SCRIPT_PATH}; cd {CWD}; exit 0',
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,universal_newlines=True)
    stdout,stderr = p.communicate()
    if stdout!='' :
        raise RuntimeError(f'ERROR: Git repo check failed with output:\n{stdout}')
    print('Repo is good : )')
    #If we've made it here all the tests passed!
    print('All tests passed!')

if __name__=='__main__' :
    main()
