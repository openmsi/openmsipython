#imports
import pathlib, logging, shutil, filecmp, os, getpass, requests, fmrest, pickle
from openmsipython.shared.logging import Logger
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.data_file_io.upload_data_file import UploadDataFile
from openmsipython.my_kafka.serialization import DataFileChunkSerializer
from openmsipython.services.install_service import write_executable_file
from openmsipython.data_models.laser_shock.config import LASER_SHOCK_CONST
from openmsipython.data_models.laser_shock.laser_shock_lab import LaserShockLab
from unittests.config import TEST_CONST

#constants
EXISTING_TEST_DATA_DIR = (pathlib.Path(__file__).parent / 'data').resolve()
NEW_TEST_DATA_DIR = (pathlib.Path(__file__).parent / 'new_test_data').resolve()
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.INFO)

#################### OTHER HELPER FUNCTIONS ####################

def prompt_to_remove(rel_filepath,prompt) :
    """
    Prompt a user about two different versions of a file and potentially 
    remove the file if they're not alright with it
    
    rel_filepath = the path to the file relevant to the new/existing test data root directory
    prompt = the prompt to give to the user to ask them whether some difference is OK
    """
    check = input(prompt)
    if check.lower() in ('n','no') :
        LOGGER.debug(f'\tremoving file {rel_filepath}')
        (NEW_TEST_DATA_DIR/rel_filepath).unlink()

def compare_and_check_old_and_new_files(filename,subdir_path='') :
    """
    Compare a newly created file with its potentially already existing counterpart 
    and double check that adding or replacing it is alright with the user

    filename = the name of the file
    subdir_path = the path to the subdirectory containing the file within the 
                  new/existing test data root directory
    """
    rel_filepath = pathlib.Path(subdir_path)/filename
    #if it's a new file
    if not (EXISTING_TEST_DATA_DIR/rel_filepath).is_file() :
        prompt_to_remove(rel_filepath,f'File {rel_filepath} would be new test data. Is that alright? [(y)/n]: ')
        return
    #if it's a different size than the older file
    old_size = (EXISTING_TEST_DATA_DIR/rel_filepath).stat().st_size
    new_size = (NEW_TEST_DATA_DIR/rel_filepath).stat().st_size
    if old_size!=new_size :
        msg = f'File {rel_filepath} has {new_size} bytes but the existing file has {old_size} bytes. '
        msg+= 'Is that alright? [(y)/n]: '
        prompt_to_remove(rel_filepath,msg)
        return
    #if it's different than what exists
    if not filecmp.cmp(EXISTING_TEST_DATA_DIR/rel_filepath,NEW_TEST_DATA_DIR/rel_filepath,shallow=False) :
        msg = f'File {rel_filepath} has different content than the existing file. Is that alright? [(y)/n]: '
        prompt_to_remove(rel_filepath,msg)
        return

def relocate_files(dirpath) :
    """
    Move any files in the given directory into the existing test data directory
    Any directories found result in calling this function again recursively
    """
    for fp in dirpath.rglob('*') :
        if fp.is_dir() :
            relocate_files(fp)
        elif fp.is_file() :
            newpath = EXISTING_TEST_DATA_DIR/(fp.relative_to(NEW_TEST_DATA_DIR))
            if not newpath.parent.is_dir() :
                newpath.parent.mkdir()
            fp.rename(EXISTING_TEST_DATA_DIR/(fp.relative_to(NEW_TEST_DATA_DIR)))

#################### INDIVIDUAL DATA CREATION FUNCTIONS ####################

def rebuild_laser_shock_filemaker_refs() :
    """
    Rebuild the pickle file containing a dictionary of some sample records 
    from each layout of the Laser Shock FileMaker database, and the corresponding 
    JSON dumps of their GEMD objects
    """
    #some constants
    RECORDS_TO_GET_BY_LAYOUT = {
        'Glass ID':[{'Glass name':'Borosilicate, T=0.25"'}],
        'Epoxy ID':[{'Epoxy Name':'Loctite Ablestik 24'}],
        'Foil ID':[{'Foil ID':'M004'}],
        'Spacer ID':[{'Spacer Name':'240um Kapton (double adhesive)'}],
        'Flyer Cutting Program':[{'Program name':'50um Al Optimized v2 (2021-10-22)'}],
        'Spacer Cutting Program':[{'Program Name':'240um Kapton Original v2 (2021-10-22)'}],
        'Flyer Stack':[{'Flyer ID': 'F071'},{'Flyer ID':'F054'}],
        'Sample':[{'Sample Name':'23-17 Mg-9Al 1Bc+3Bc ECAE Plate'}],
        'Launch Package':[{'Launch ID':'F071-R2C2-Spacer-Sample'},{'Launch ID':'F054-R3C2-Spacer'}],
        'Experiment':[{'Launch ID':'F071-R2C2-Spacer-Sample'},{'Launch ID':'F054-R3C2-Spacer'}],
        }
    #get JHED credentials to authenticate to the FileMaker Database
    username = os.path.expandvars('$JHED_UNAME')
    if username=='$JHED_UNAME' :
        username = (input('Please enter your JHED username: ')).rstrip()
    password = os.path.expandvars('$JHED_PWORD')
    if password=='$JHED_PWORD' :
        password = getpass.getpass(f'Please enter the JHED password for {username}: ')
    #disable warnings
    requests.packages.urllib3.disable_warnings()
    #start up the dictionary that will be saved
    filemaker_records = {}
    #get requested records from each of the layouts and add them to the dictionary
    for layout_name,query in RECORDS_TO_GET_BY_LAYOUT.items() : 
        if layout_name not in filemaker_records.keys() :
            filemaker_records[layout_name] = []
        #create the server and login to it
        try :
            fms = fmrest.Server(LASER_SHOCK_CONST.FILEMAKER_SERVER_IP_ADDRESS,
                                user=username,
                                password=password,
                                database=LASER_SHOCK_CONST.DATABASE_NAME,
                                layout=layout_name,
                                verify_ssl=False,
                                )
            #login
            fms.login()
        except Exception as e :
            errmsg = f'ERROR: could not connect to {LASER_SHOCK_CONST.DATABASE_NAME} FileMaker Database at IP '
            errmsg+= f'{LASER_SHOCK_CONST.FILEMAKER_SERVER_IP_ADDRESS}. Please check the network you are on and '
            errmsg+= f'the login credentials you provided to make sure you have access. Exception: {e}'
            LOGGER.error(errmsg,RuntimeError)
        #get the records
        if len(query)>0 :
            try :
                foundset = fms.find(query)
            except Exception :
                LOGGER.warning(f'finding records in {layout_name} layout matching query {query} would have crashed')
                foundset = []
            for record in foundset :
                record_dict = {}
                for key, value in zip(record.keys(),record.values()) :
                    record_dict[key] = value
                filemaker_records[layout_name].append(record_dict)
        if len(filemaker_records[layout_name])<=0 :
            LOGGER.warning(f'WARNING: no records found in {layout_name} layout matching query {query}')
    #write out the entire dictionary as a pickle file
    with open(NEW_TEST_DATA_DIR/TEST_CONST.FILEMAKER_RECORD_PICKLE_FILENAME,'wb') as fp :
        pickle.dump(filemaker_records,fp,protocol=pickle.HIGHEST_PROTOCOL)
    compare_and_check_old_and_new_files((NEW_TEST_DATA_DIR/TEST_CONST.FILEMAKER_RECORD_PICKLE_FILENAME).name)
    #Run the LaserShockLab to create GEMD constructs and dump them as .json files
    lsl = LaserShockLab(dirpath=NEW_TEST_DATA_DIR/TEST_CONST.LASER_SHOCK_DATA_MODEL_OUTPUT_DIRNAME)
    lsl.create_gemd_objects(records_dict=filemaker_records)
    lsl.dump_to_json_files(complete_histories=True,recursive=False,indent=2)
    for fp in (NEW_TEST_DATA_DIR/TEST_CONST.LASER_SHOCK_DATA_MODEL_OUTPUT_DIRNAME).glob('*') :
        if fp.name.startswith('LaserShock') and not fp.name.endswith('.log') :
            compare_and_check_old_and_new_files(fp.name,fp.parent.name)
        else :
            fp.unlink()

def rebuild_binary_file_chunks_for_serialization_reference() :
    """
    Rebuild the binary file chunks to reference for serialization/deserialization tests
    """
    #path to the test data file
    test_data_fp = EXISTING_TEST_DATA_DIR/TEST_CONST.TEST_DATA_FILE_ROOT_DIR_NAME/TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME
    test_data_fp = test_data_fp/TEST_CONST.TEST_DATA_FILE_NAME
    #make the data file and build its list of chunks
    df = UploadDataFile(test_data_fp,rootdir=EXISTING_TEST_DATA_DIR/TEST_CONST.TEST_DATA_FILE_ROOT_DIR_NAME,
                        logger=LOGGER)
    df._build_list_of_file_chunks(RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
    #populate and serialize a few chunks and save them as binary data
    dfcs = DataFileChunkSerializer()
    for i in range(3) :
        df.chunks_to_upload[i].populate_with_file_data(LOGGER)
        binary_data = dfcs(df.chunks_to_upload[i])
        fn = f'{TEST_CONST.TEST_DATA_FILE_NAME.split(".")[0]}_test_chunk_{i}.bin'
        with open(NEW_TEST_DATA_DIR/fn,'wb') as fp :
            fp.write(binary_data)
        compare_and_check_old_and_new_files(fn)

def rebuild_test_services_executable() :
    """
    Rebuild the executable file used to double-check Services behavior
    """
    #some constants
    TEST_SERVICE_NAME = 'DataFileUploadDirectoryService'
    TEST_SERVICE_EXECUTABLE_ARGSLIST = ['test_upload']
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
        LOGGER.info('Rebuilding Laser Shock Lab record file and .json dumps....')
        rebuild_laser_shock_filemaker_refs()
        LOGGER.info(f'Moving new files into {EXISTING_TEST_DATA_DIR}...')
        relocate_files(NEW_TEST_DATA_DIR)
    except Exception as e :
        raise e 
    finally :
        shutil.rmtree(NEW_TEST_DATA_DIR)

if __name__=='__main__' :
    main()



