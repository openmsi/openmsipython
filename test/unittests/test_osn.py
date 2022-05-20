#imports
import unittest, pathlib, time, logging, shutil

from openmsipython.osn.osn_stream_processor import OSNStreamProcessor
from openmsipython.shared.logging import Logger
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.data_file_io.data_file_upload_directory import DataFileUploadDirectory
from config import TEST_CONST
from utilities import MyThread

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)
UPDATE_SECS = 5
TIMEOUT_SECS = 90
JOIN_TIMEOUT_SECS = 60
TOPIC_NAME = 'osn_test'

class TestOSN(unittest.TestCase) :
    """
    Class for testing DataFileUploadDirectory and DataFileDownloadDirectory functions
    """

    #called by the test method below
    def run_data_file_upload_directory(self) :
        #make the directory to watch
        dfud = DataFileUploadDirectory(TEST_CONST.TEST_WATCHED_DIR_PATH,update_secs=UPDATE_SECS,logger=LOGGER)
        #start upload_files_as_added in a separate thread so we can time it out
        upload_thread = MyThread(target=dfud.upload_files_as_added,
                                 args=(TEST_CONST.TEST_CONFIG_FILE_PATH,TOPIC_NAME),
                                 kwargs={'n_threads':RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                         'chunk_size':RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                         'max_queue_size':RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE,
                                         'upload_existing':True})


        upload_thread.start()
        try :
            #wait a second, copy the test file into the watched directory, and wait another second
            time.sleep(1)
            fp = TEST_CONST.TEST_WATCHED_DIR_PATH/TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME/TEST_CONST.TEST_DATA_FILE_NAME
            if not fp.parent.is_dir() :
                fp.parent.mkdir(parents=True)
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
    def upload_data_into_osn(self) :
        #make the directory to reconstruct files into
        # TEST_CONST.TEST_RECO_DIR_PATH.mkdir()
        #start up the DataFileDownloadDirectory
        osp = OSNStreamProcessor(
            TEST_CONST.TEST_BUCKET_NAME,
                                         TEST_CONST.TEST_CONFIG_FILE_PATH,
                                         TOPIC_NAME,
                                         n_threads=RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS,
                                         update_secs=UPDATE_SECS,
                                         consumer_group_ID='consumer_group_ID',
                                         logger=LOGGER,
                                         )
        # cls.bucket_name = args.bucket_name
        msg = f'Listening to the {TOPIC_NAME} topic to find Lecroy data files and create '
        LOGGER.info(msg)
        # n_read, n_processed = osn_stream_proc.make_stream()
        # n_read, n_processed = \
        osp.make_stream()
        osp.close()
        # # shut down when that function returns
        # msg = ''
        # if args.output_dir is not None:
        #     msg += f'writing to {args.output_dir} '
        # msg += 'shut down'
        # osn_stream_proc.logger.info(msg)
        # msg = f'{n_read} total messages were consumed'
        # osn_stream_proc.logger.info(msg)

    #below we test both upload_files_as_added and then reconstruct, in that order
    def test_upload_kafka_and_trasnfer_into_osn_kafka(self) :
        self.run_data_file_upload_directory()
        self.upload_data_into_osn()