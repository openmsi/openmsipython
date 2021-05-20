#imports
from config import TEST_CONST
from openmsipython.data_file_io.data_file_directory import DataFileDirectory
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.utilities.logging import Logger
from threading import Thread
import unittest, pathlib, time, logging, shutil, filecmp

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)
UPDATE_SECS = 5
TIMEOUT_SECS = 60

class TestDataFileDirectory(unittest.TestCase) :
    """
    Class for testing DataFileDirectory functions
    """

    #called by the test method below
    def run_upload_files_as_added(self) :
        #make the directory to watch
        TEST_CONST.TEST_WATCHED_DIR_PATH.mkdir()
        try :
            #start up the DataFileDirectory
            dfd = DataFileDirectory(TEST_CONST.TEST_WATCHED_DIR_PATH,logger=LOGGER)
            #start upload_files_as_added in a separate thread so we can time it out
            upload_thread = Thread(target=dfd.upload_files_as_added,
                                   args=(TEST_CONST.TEST_CONFIG_FILE_PATH,RUN_OPT_CONST.DEFAULT_TOPIC_NAME),
                                   kwargs={'n_threads':RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                           'chunk_size':RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                           'max_queue_size':RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE,
                                           'update_secs':UPDATE_SECS,
                                           'new_files_only':False}
                                  )
            upload_thread.start()
            #wait a second, and then copy the test file into the watched directory
            time.sleep(1)
            (TEST_CONST.TEST_WATCHED_DIR_PATH/TEST_CONST.TEST_DATA_FILE_NAME).write_bytes(TEST_CONST.TEST_DATA_FILE_PATH.read_bytes())
            #put the "check" command into the input queue a couple times
            dfd.user_input_queue.put('c')
            dfd.user_input_queue.put('check')
            #put the "quit" command into the input queue, which SHOULD stop the method running
            LOGGER.set_stream_level(logging.INFO)
            LOGGER.info(f'\nQuitting upload thread in run_upload_files_as_added; will timeout after {TIMEOUT_SECS} seconds....')
            LOGGER.set_stream_level(logging.ERROR)
            dfd.user_input_queue.put('q')
            #wait for the uploading thread to complete
            upload_thread.join(timeout=TIMEOUT_SECS)
            if upload_thread.is_alive() :
                raise TimeoutError(f'ERROR: upload thread in run_upload_files_as_added timed out after {TIMEOUT_SECS} seconds!')
        except Exception as e :
            raise e
        finally :
            shutil.rmtree(TEST_CONST.TEST_WATCHED_DIR_PATH)

    #called by the test method below
    def run_reconstruct(self) :
        #make the directory to reconstruct files into
        TEST_CONST.TEST_RECO_DIR_PATH.mkdir()
        try :
            #start up the DataFileDirectory
            dfd = DataFileDirectory(TEST_CONST.TEST_RECO_DIR_PATH,logger=LOGGER)
            #start reconstruct in a separate thread so we can time it out
            download_thread = Thread(target=dfd.reconstruct,
                                     args=(TEST_CONST.TEST_CONFIG_FILE_PATH,RUN_OPT_CONST.DEFAULT_TOPIC_NAME),
                                     kwargs={'n_threads':RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                             'update_secs':UPDATE_SECS}
                                    )
            download_thread.start()
            #put the "check" command into the input queue a couple times
            dfd.user_input_queue.put('c')
            dfd.user_input_queue.put('check')
            #wait for the timeout for the test file to be completely reconstructed or for the reconstructor to stop getting new messages
            current_messages_read = -1
            time_waited = 0
            LOGGER.set_stream_level(logging.INFO)
            LOGGER.info(f'Waiting to reconstruct test file from the "{RUN_OPT_CONST.DEFAULT_TOPIC_NAME}" topic in run_reconstruct (will timeout after {TIMEOUT_SECS} seconds)...')
            LOGGER.set_stream_level(logging.ERROR)
            while len(dfd._completely_reconstructed_filenames)==0 and current_messages_read<dfd._n_msgs_read and time_waited<TIMEOUT_SECS:
                current_messages_read = dfd._n_msgs_read
                LOGGER.set_stream_level(logging.INFO)
                LOGGER.info(f'\t{current_messages_read} messages read after waiting {time_waited} seconds....')
                LOGGER.set_stream_level(logging.ERROR)
                time.sleep(5)
                time_waited+=5
            #After timing out, stalling, or completely reconstructing the test file, put the "quit" command into the input queue, which SHOULD stop the method running
            LOGGER.set_stream_level(logging.INFO)
            LOGGER.info('Quitting download thread in run_reconstruct; will timeout after 5 seconds....')
            LOGGER.set_stream_level(logging.ERROR)
            dfd.user_input_queue.put('q')
            #wait for the download thread to finish
            download_thread.join(timeout=5)
            if download_thread.is_alive() :
                raise TimeoutError('ERROR: download thread in run_reconstruct timed out after 5 seconds!')
            #make sure the reconstructed file exists with the same name and content as the original
            self.assertTrue((TEST_CONST.TEST_RECO_DIR_PATH/TEST_CONST.TEST_DATA_FILE_NAME).is_file())
            if not filecmp.cmp(TEST_CONST.TEST_DATA_FILE_PATH,TEST_CONST.TEST_RECO_DIR_PATH/TEST_CONST.TEST_DATA_FILE_NAME,shallow=False) :
                raise RuntimeError(f'ERROR: files are not the same after reconstruction! (This may also be due to the timeout at {TIMEOUT_SECS} seconds)')
        except Exception as e :
            raise e
        finally :
            shutil.rmtree(TEST_CONST.TEST_RECO_DIR_PATH)

    #below we test both upload_files_as_added and then reconstruct, in that order
    def test_upload_files_as_added_and_then_reconstruct(self) :
        self.run_upload_files_as_added()
        self.run_reconstruct()

    def test_filepath_should_be_uploaded(self) :
        dfd = DataFileDirectory(TEST_CONST.TEST_DATA_DIR_PATH,logger=LOGGER)
        LOGGER.set_stream_level(logging.INFO)
        LOGGER.info('\nExpecting three errors below:')
        LOGGER.set_stream_level(logging.ERROR)
        with self.assertRaises(TypeError) :
            dfd._filepath_should_be_uploaded(None)
        with self.assertRaises(TypeError) :
            dfd._filepath_should_be_uploaded(5)
        with self.assertRaises(TypeError) :
            dfd._filepath_should_be_uploaded('this is a string not a path!')
        self.assertFalse(dfd._filepath_should_be_uploaded(TEST_CONST.TEST_DATA_DIR_PATH/'.this_file_is_hidden'))
        self.assertFalse(dfd._filepath_should_be_uploaded(TEST_CONST.TEST_DATA_DIR_PATH/'this_file_is_a_log_file.log'))
        for fp in TEST_CONST.TEST_DATA_DIR_PATH.glob('*') :
            if fp.name.startswith('.') or fp.name.endswith('.log') :
                self.assertFalse(dfd._filepath_should_be_uploaded(fp.resolve()))
            else :
                self.assertTrue(dfd._filepath_should_be_uploaded(fp.resolve()))
