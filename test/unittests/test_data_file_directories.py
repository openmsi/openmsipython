#imports
import unittest, pathlib, time, logging, shutil, filecmp
from openmsipython.shared.logging import Logger
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.data_file_io.data_file_upload_directory import DataFileUploadDirectory
from openmsipython.data_file_io.data_file_download_directory import DataFileDownloadDirectory
from config import TEST_CONST
from utilities import MyThread

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)
UPDATE_SECS = 5
TIMEOUT_SECS = 90
JOIN_TIMEOUT_SECS = 60
TOPIC_NAME = 'test_data_file_directories'

class TestDataFileDirectories(unittest.TestCase) :
    """
    Class for testing DataFileUploadDirectory and DataFileDownloadDirectory functions
    """

    #called by the test method below
    def run_data_file_upload_directory(self) :
        #make the directory to watch
        (TEST_CONST.TEST_WATCHED_DIR_PATH/TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME).mkdir(parents=True)
        #start up the DataFileUploadDirectory
        dfud = DataFileUploadDirectory(TEST_CONST.TEST_WATCHED_DIR_PATH,update_secs=UPDATE_SECS,logger=LOGGER)
        #start upload_files_as_added in a separate thread so we can time it out
        upload_thread = MyThread(target=dfud.upload_files_as_added,
                                 args=(TEST_CONST.TEST_CONFIG_FILE_PATH,TOPIC_NAME),
                                 kwargs={'n_threads':RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                         'chunk_size':RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                         'max_queue_size':RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE,
                                         'new_files_only':False}
                                )
        upload_thread.start()
        try :
            #wait a second, copy the test file into the watched directory, and wait another second
            time.sleep(1)
            fp = TEST_CONST.TEST_WATCHED_DIR_PATH/TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME/TEST_CONST.TEST_DATA_FILE_NAME
            fp.write_bytes(TEST_CONST.TEST_DATA_FILE_PATH.read_bytes())
            time.sleep(1)
            #put the "check" command into the input queue a couple times to test it
            dfud.control_command_queue.put('c')
            dfud.control_command_queue.put('check')
            #put the quit command in the command queue to stop the process running
            LOGGER.set_stream_level(logging.INFO)
            msg = '\nQuitting upload thread in run_data_file_upload_directory; '
            msg+= f'will timeout after {TIMEOUT_SECS} seconds....'
            LOGGER.info(msg)
            LOGGER.set_stream_level(logging.ERROR)
            dfud.control_command_queue.put('q')
            #wait for the uploading thread to complete
            upload_thread.join(timeout=TIMEOUT_SECS)
            if upload_thread.is_alive() :
                errmsg = 'ERROR: upload thread in run_data_file_upload_directory '
                errmsg+= f'timed out after {TIMEOUT_SECS} seconds!'
                raise TimeoutError(errmsg)
        except Exception as e :
            raise e
        finally :
            if upload_thread.is_alive() :
                try :
                    dfud.shutdown()
                    upload_thread.join(timeout=JOIN_TIMEOUT_SECS)
                    if upload_thread.is_alive() :
                        errmsg = 'ERROR: upload thread in run_data_file_upload_directory timed out after '
                        errmsg+= f'{JOIN_TIMEOUT_SECS} seconds!'
                        raise TimeoutError(errmsg)
                except Exception as e :
                    raise e
                finally :
                    shutil.rmtree(TEST_CONST.TEST_WATCHED_DIR_PATH)
            if TEST_CONST.TEST_WATCHED_DIR_PATH.is_dir() :
                shutil.rmtree(TEST_CONST.TEST_WATCHED_DIR_PATH)

    #called by the test method below
    def run_data_file_download_directory(self) :
        #make the directory to reconstruct files into
        TEST_CONST.TEST_RECO_DIR_PATH.mkdir()
        #start up the DataFileDownloadDirectory
        dfdd = DataFileDownloadDirectory(TEST_CONST.TEST_RECO_DIR_PATH,
                                         TEST_CONST.TEST_CONFIG_FILE_PATH,
                                         TOPIC_NAME,
                                         n_threads=RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS,
                                         update_secs=UPDATE_SECS,
                                         consumer_group_ID='run_data_file_download_directory',
                                         logger=LOGGER,
                                         )
        #start reconstruct in a separate thread so we can time it out
        download_thread = MyThread(target=dfdd.reconstruct)
        download_thread.start()
        try :
            #put the "check" command into the input queue a couple times
            dfdd.control_command_queue.put('c')
            dfdd.control_command_queue.put('check')
            #wait for the timeout for the test file to be completely reconstructed 
            #or for the reconstructor to stop getting new messages
            current_messages_read = -1
            time_waited = 0
            LOGGER.set_stream_level(logging.INFO)
            msg = f'Waiting to reconstruct test file from the "{TOPIC_NAME}" topic in run_data_file_download_directory '
            msg+= f'(will timeout after {TIMEOUT_SECS} seconds)...'
            LOGGER.info(msg)
            LOGGER.set_stream_level(logging.ERROR)
            while ( (TEST_CONST.TEST_DATA_FILE_NAME not in dfdd.completely_reconstructed_filepaths) and 
                    current_messages_read<dfdd.n_msgs_read and time_waited<TIMEOUT_SECS ) :
                current_messages_read = dfdd.n_msgs_read
                LOGGER.set_stream_level(logging.INFO)
                LOGGER.info(f'\t{current_messages_read} messages read after waiting {time_waited} seconds....')
                LOGGER.set_stream_level(logging.ERROR)
                time.sleep(5)
                time_waited+=5
            #After timing out, stalling, or completely reconstructing the test file, 
            #put the "quit" command into the input queue, which SHOULD stop the method running
            LOGGER.set_stream_level(logging.INFO)
            msg = f'Quitting download thread in run_data_file_download_directory after reading {dfdd.n_msgs_read} '
            msg+= f'messages; will timeout after {JOIN_TIMEOUT_SECS} seconds....'
            LOGGER.info(msg)
            LOGGER.set_stream_level(logging.ERROR)
            dfdd.control_command_queue.put('q')
            #wait for the download thread to finish
            download_thread.join(timeout=JOIN_TIMEOUT_SECS)
            if download_thread.is_alive() :
                errmsg = 'ERROR: download thread in run_data_file_download_directory timed out after '
                errmsg+= f'{JOIN_TIMEOUT_SECS} seconds!'
                raise TimeoutError(errmsg)
            #make sure the reconstructed file exists with the same name and content as the original
            fp = TEST_CONST.TEST_RECO_DIR_PATH/TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME/TEST_CONST.TEST_DATA_FILE_NAME
            self.assertTrue(fp.is_file())
            if not filecmp.cmp(TEST_CONST.TEST_DATA_FILE_PATH,fp,shallow=False) :
                errmsg = 'ERROR: files are not the same after reconstruction! '
                errmsg+= f'(This may also be due to the timeout at {TIMEOUT_SECS} seconds)'
                raise RuntimeError(errmsg)
        except Exception as e :
            raise e
        finally :
            if download_thread.is_alive() :
                try :
                    dfdd.control_command_queue.put('q')
                    download_thread.join(timeout=JOIN_TIMEOUT_SECS)
                    if download_thread.is_alive() :
                        errmsg = 'ERROR: download thread in run_data_file_download_directory timed out after '
                        errmsg+= f'{JOIN_TIMEOUT_SECS} seconds!'
                        raise TimeoutError(errmsg)
                except Exception as e :
                    raise e
                finally :
                    shutil.rmtree(TEST_CONST.TEST_RECO_DIR_PATH)
            if TEST_CONST.TEST_RECO_DIR_PATH.is_dir() :
                shutil.rmtree(TEST_CONST.TEST_RECO_DIR_PATH)

    #below we test both upload_files_as_added and then reconstruct, in that order
    def test_upload_and_download_directories_kafka(self) :
        self.run_data_file_upload_directory()
        self.run_data_file_download_directory()

    def test_filepath_should_be_uploaded(self) :
        dfd = DataFileUploadDirectory(TEST_CONST.TEST_DATA_DIR_PATH,logger=LOGGER)
        LOGGER.set_stream_level(logging.INFO)
        LOGGER.info('\nExpecting three errors below:')
        LOGGER.set_stream_level(logging.ERROR)
        with self.assertRaises(TypeError) :
            dfd.filepath_should_be_uploaded(None)
        with self.assertRaises(TypeError) :
            dfd.filepath_should_be_uploaded(5)
        with self.assertRaises(TypeError) :
            dfd.filepath_should_be_uploaded('this is a string not a path!')
        self.assertFalse(dfd.filepath_should_be_uploaded(TEST_CONST.TEST_DATA_DIR_PATH/'.this_file_is_hidden'))
        self.assertFalse(dfd.filepath_should_be_uploaded(TEST_CONST.TEST_DATA_DIR_PATH/'this_file_is_a_log_file.log'))
        for fp in TEST_CONST.TEST_DATA_DIR_PATH.rglob('*') :
            check = True
            if fp.is_dir() :
                check=False
            elif fp.name.startswith('.') or fp.name.endswith('.log') :
                check=False
            self.assertEqual(dfd.filepath_should_be_uploaded(fp.resolve()),check)
        subdir_path = TEST_CONST.TEST_DATA_DIR_PATH / 'this_subdirectory_should_not_be_uploaded'
        subdir_path.mkdir()
        try :
            self.assertFalse(dfd.filepath_should_be_uploaded(subdir_path))
        except Exception as e :
            raise e
        finally : 
            shutil.rmtree(subdir_path)