#imports
from openmsipython.my_kafka.serialization import DataFileChunkSerializer
from openmsipython.data_file_io.data_file import UploadDataFile
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.utilities.logging import Logger
import pathlib, logging, shutil, filecmp

#constants
EXISTING_TEST_DATA_DIR = (pathlib.Path(__file__).parent / 'data').resolve()
TEST_DATA_FILE_ROOTDIR_NAME = 'test_file_root_dir'
TEST_DATA_FILE_SUBDIR_NAME = 'test_file_sub_dir'
TEST_DATA_FILE_NAME = '1a0ceb89-b5f0-45dc-9c12-63d3020e2217.dat'
NEW_TEST_DATA_DIR = (pathlib.Path(__file__).parent / 'new_test_data').resolve()
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)


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
        prompt_to_remove(filename_or_path,f'File {filename_or_path} has {new_size} bytes but the existing file has {old_size} bytes. Is that alright? [(y)/n]: ')
        return
    #if it's different than what exists
    if not filecmp.cmp(EXISTING_TEST_DATA_DIR/filename_or_path,NEW_TEST_DATA_DIR/filename_or_path,shallow=False) :
        prompt_to_remove(filename_or_path,f'File {filename_or_path} has different content than the existing file. Is that alright? [(y)/n]: ')
        return

#################### INDIVIDUAL DATA CREATION FUNCTIONS ####################

#rebuild the binary file chunks to reference for serialization/deserialization tests
def rebuild_binary_file_chunks_for_serialization_reference() :
    test_data_file_path = EXISTING_TEST_DATA_DIR / TEST_DATA_FILE_ROOTDIR_NAME / TEST_DATA_FILE_SUBDIR_NAME / TEST_DATA_FILE_NAME
    #make the data file and build its list of chunks
    df = UploadDataFile(test_data_file_path,rootdir=EXISTING_TEST_DATA_DIR/TEST_DATA_FILE_ROOTDIR_NAME,logger=LOGGER)
    df._build_list_of_file_chunks(RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
    #populate and serialize a few chunks and save them as binary data
    dfcs = DataFileChunkSerializer()
    for i in range(3) :
        df._chunks_to_upload[i]._populate_with_file_data(LOGGER)
        binary_data = dfcs(df._chunks_to_upload[i])
        fn = f'{TEST_DATA_FILE_NAME.split(".")[0]}_test_chunk_{i}.bin'
        with open(NEW_TEST_DATA_DIR/fn,'wb') as fp :
            fp.write(binary_data)
        compare_and_check_old_and_new_files(fn)

#################### MAIN SCRIPT ####################

def main() :
    #make the directory to hold the new test data
    NEW_TEST_DATA_DIR.mkdir()
    #try populating it with all of the necessary new data, checking with the user along the way
    try :
        print('Rebuilding reference binary file chunks....')
        rebuild_binary_file_chunks_for_serialization_reference()
        print(f'Moving new files into {EXISTING_TEST_DATA_DIR}...')
        for fp in NEW_TEST_DATA_DIR.rglob('*') :
            (NEW_TEST_DATA_DIR/fp.name).replace(EXISTING_TEST_DATA_DIR/fp.name)
    except Exception as e :
        raise e 
    finally :
        shutil.rmtree(NEW_TEST_DATA_DIR)

if __name__=='__main__' :
    main()



