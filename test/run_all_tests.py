#imports
from argparse import ArgumentParser
import subprocess, pathlib

#constants
TOP_DIR_PATH = (pathlib.Path(__file__).parent.parent).resolve()
UNITTEST_DIR_PATH = (pathlib.Path(__file__).parent / 'unittests').resolve()
TEST_REPO_STATUS_SCRIPT_PATH = (pathlib.Path(__file__).parent / 'test_repo_status.sh').resolve()
CWD = pathlib.Path().resolve()

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    parser.add_argument('--no_pyflakes', action='store_true',
                        help='Add this flag to skip running the pyflakes check')
    unittest_opts = parser.add_mutually_exclusive_group()
    unittest_opts.add_argument('--no_unittests', action='store_true',
                               help='Add this flag to skip running the unittest checks')
    unittest_opts.add_argument('--no_kafka', action='store_true',
                               help='Add this flag to skip running the unittest checks')
    parser.add_argument('--no_repo', action='store_true',
                        help='Add this flag to skip running the Git repository checks')
    args = parser.parse_args(args=args)
    #test pyflakes
    if args.no_pyflakes :
        print('SKIPPING PYFLAKES TEST')
    else :
        print('testing code consistency with pyflakes...')
        p = subprocess.Popen(f'cd {TOP_DIR_PATH}; pyflakes .; cd {CWD}; exit 0',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,universal_newlines=True)
        stdout,stderr = p.communicate()
        if stdout!='' :
            raise RuntimeError(f'ERROR: pyflakes check failed with output:\n{stdout}')
        print('Passed pyflakes check : )')
    #perform all the unittests
    if args.no_unittests :
        print('SKIPPING UNITTESTS')
    else :
        print(f'Running all unittests in {UNITTEST_DIR_PATH}...')
        cmd = f'python -m unittest discover -s {UNITTEST_DIR_PATH} -v'
        if args.no_kafka :
            cmd+=' -p test*parallel.py'
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True,universal_newlines=True)
        for stdout_line in p.stdout :
            print(stdout_line,end='')
        return_code = p.wait()
        if return_code>0 :
            raise RuntimeError('ERROR: some unittest(s) failed! See output above for details.')
            return
        print('All unittest checks complete : )')
    if args.no_repo :
        print('SKIPPING GIT REPOSITORY CHECKS')
    else :
        #make sure the Github repo is still clean from its initial state
        print('Checking the status of the Git repo....')
        p = subprocess.Popen(f'cd {TOP_DIR_PATH}; sh {TEST_REPO_STATUS_SCRIPT_PATH}; cd {CWD}; exit 0',
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,universal_newlines=True)
        stdout,stderr = p.communicate()
        if stdout!='' :
            raise RuntimeError(f'ERROR: Git repo check failed with output:\n{stdout}')
        print('Repo is good : )')
    #If we've made it here all the (requested) tests passed!
    msg = 'All '
    if args.no_pyflakes or args.no_unittests or args.no_repo :
        msg+='requested '
    msg+='tests passed!'
    print(msg)

if __name__=='__main__' :
    main()
