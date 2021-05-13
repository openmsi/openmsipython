#imports
import subprocess, pathlib

#constants
TOP_DIR_PATH = (pathlib.Path(__file__).parent.parent).resolve()
UNITTEST_DIR_PATH = (pathlib.Path(__file__).parent / 'unittests').resolve()
CWD = pathlib.Path().resolve()

def main() :
    #test pyflakes
    print('testing code consistency with pyflakes...')
    p = subprocess.Popen(f'cd {TOP_DIR_PATH}; pyflakes .; cd {CWD}; exit 0',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    stdout,stderr = p.communicate()
    if stdout.decode()!='' :
        raise RuntimeError(f'ERROR: pyflakes check failed with output:\n{stdout.decode()}')
    print('Passed pyflakes check : )')
    #perform all the unittests
    print(f'Running all unittests in {UNITTEST_DIR_PATH}...')
    try :
        subprocess.check_output(f'python -m unittest discover -s {UNITTEST_DIR_PATH} -v',stderr=subprocess.STDOUT,shell=True)
    except subprocess.CalledProcessError as e :
        raise RuntimeError(f'ERROR: some unittest(s) failed with output:\n{e.output.decode()}')
    print('All unittest checks complete : )')

if __name__=='__main__' :
    main()
