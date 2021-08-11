#imports
import pathlib, logging, shutil, filecmp
from openmsipython.utilities.logging import Logger
from openmsipython.my_kafka.serialization import DataFileChunkSerializer
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.data_file_io.upload_data_file import UploadDataFile
from openmsipython.services.install_service import write_executable_file

#constants
EXISTING_TEST_DATA_DIR = (pathlib.Path(__file__).parent / 'data').resolve()
TEST_DATA_FILE_ROOTDIR_NAME = 'test_file_root_dir'
TEST_DATA_FILE_SUBDIR_NAME = 'test_file_sub_dir'
TEST_DATA_FILE_NAME = '1a0ceb89-b5f0-45dc-9c12-63d3020e2217.dat'
NEW_TEST_DATA_DIR = (pathlib.Path(__file__).parent / 'new_test_data').resolve()
TEST_SERVICE_NAME = 'DataFileUploadDirectoryService'
TEST_SERVICE_EXECUTABLE_ARGSLIST = ['test_upload']
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.INFO)


#################### OTHER HELPER FUNCTIONS ####################

#prompt a user about two different versions of a file and potentially remove the file if they're not alright with it
def prompt_to_remove(filename,prompt) :
    check = input(prompt)
    if check.lower() in ('n','no') :
        print(f'\tremoving file {filename}')
        (NEW_TEST_DATA_DIR/filename).unlink()

#compare a newly created file with its potentially already existing counterpart 
#and double check that adding or replacing it is alright with the user
def compare_and_check_old_and_new_files(filename_or_path) :
    #if it's a new file
    if not (EXISTING_TEST_DATA_DIR/filename_or_path).is_file() :
        prompt_to_remove(filename_or_path,f'File {filename_or_path} would be new test data. Is that alright? [(y)/n]: ')
        return
    #if it's a different size than the older file
    old_size = (EXISTING_TEST_DATA_DIR/filename_or_path).stat().st_size
    new_size = (NEW_TEST_DATA_DIR/filename_or_path).stat().st_size
    if old_size!=new_size :
        msg = f'File {filename_or_path} has {new_size} bytes but the existing file has {old_size} bytes. '
        msg+= 'Is that alright? [(y)/n]: '
        prompt_to_remove(filename_or_path,msg)
        return
    #if it's different than what exists
    if not filecmp.cmp(EXISTING_TEST_DATA_DIR/filename_or_path,NEW_TEST_DATA_DIR/filename_or_path,shallow=False) :
        msg = f'File {filename_or_path} has different content than the existing file. Is that alright? [(y)/n]: '
        prompt_to_remove(filename_or_path,msg)
        return

#################### INDIVIDUAL DATA CREATION FUNCTIONS ####################

#rebuild the binary file chunks to reference for serialization/deserialization tests
def rebuild_binary_file_chunks_for_serialization_reference() :
    test_data_fp = EXISTING_TEST_DATA_DIR/TEST_DATA_FILE_ROOTDIR_NAME/TEST_DATA_FILE_SUBDIR_NAME/TEST_DATA_FILE_NAME
    #make the data file and build its list of chunks
    df = UploadDataFile(test_data_fp,rootdir=EXISTING_TEST_DATA_DIR/TEST_DATA_FILE_ROOTDIR_NAME,logger=LOGGER)
    df._build_list_of_file_chunks(RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
    #populate and serialize a few chunks and save them as binary data
    dfcs = DataFileChunkSerializer()
    for i in range(3) :
        df.chunks_to_upload[i]._populate_with_file_data(LOGGER)
        binary_data = dfcs(df.chunks_to_upload[i])
        fn = f'{TEST_DATA_FILE_NAME.split(".")[0]}_test_chunk_{i}.bin'
        with open(NEW_TEST_DATA_DIR/fn,'wb') as fp :
            fp.write(binary_data)
        compare_and_check_old_and_new_files(fn)

#rebuild the executable file used to double-check Services behavior
def rebuild_test_services_executable() :
    #create the file using the function supplied
    write_executable_file(TEST_SERVICE_NAME,TEST_SERVICE_EXECUTABLE_ARGSLIST)
    #move it to the new test data folder
    exec_fp = pathlib.Path(__file__).parent.parent/'openmsipython'/'services'/'working_dir'
    exec_fp = exec_fp/f'{TEST_SERVICE_NAME}_python_executable.py'
    exec_fp.replace(NEW_TEST_DATA_DIR/exec_fp.name)
    compare_and_check_old_and_new_files(exec_fp.name)

#################### MAIN SCRIPT ####################

def main() :
    #make the directory to hold the new test data
    NEW_TEST_DATA_DIR.mkdir()
    #try populating it with all of the necessary new data, checking with the user along the way
    try :
        LOGGER.info('Rebuilding reference binary file chunks....')
        rebuild_binary_file_chunks_for_serialization_reference()
        LOGGER.info('Rebuilding reference Service executable file....')
        rebuild_test_services_executable()
        LOGGER.info(f'Moving new files into {EXISTING_TEST_DATA_DIR}...')
        for fp in NEW_TEST_DATA_DIR.rglob('*') :
            (NEW_TEST_DATA_DIR/fp.name).replace(EXISTING_TEST_DATA_DIR/fp.name)
    except Exception as e :
        raise e 
    finally :
        shutil.rmtree(NEW_TEST_DATA_DIR)

if __name__=='__main__' :
    main()



