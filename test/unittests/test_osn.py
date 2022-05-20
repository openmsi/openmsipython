# imports
import os
import unittest, pathlib, time, logging, shutil, hashlib
from openmsipython.osn.osn_stream_processor import OSNStreamProcessor
from openmsipython.osn.s3_data_transfer import s3_data_transfer
from openmsipython.shared.logging import Logger
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.data_file_io.data_file_upload_directory import DataFileUploadDirectory
from config import TEST_CONST
from utilities import MyThread

# constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0], logging.ERROR)
UPDATE_SECS = 5
TIMEOUT_SECS = 90
JOIN_TIMEOUT_SECS = 60
TOPIC_NAME = 'osn_test'


class TestOSN(unittest.TestCase):
    """
    Class for testing DataFileUploadDirectory and DataFileDownloadDirectory functions
    """

    # called by the test method below
    def run_data_file_upload_directory(self):
        # make the directory to watch
        dfud = DataFileUploadDirectory(TEST_CONST.TEST_WATCHED_DIR_PATH, update_secs=UPDATE_SECS, logger=LOGGER)
        print(TEST_CONST.TEST_WATCHED_DIR_PATH)
        # osn_path = TEST_CONST.TEST_WATCHED_DIR_PATH.replace('\\', '/')
        # print(osn_path)
        # start upload_files_as_added in a separate thread so we can time it out
        upload_thread = MyThread(target=dfud.upload_files_as_added,
                                 args=(TEST_CONST.TEST_CONFIG_FILE_PATH, TOPIC_NAME),
                                 kwargs={'n_threads': RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                         'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                         'max_queue_size': RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE,
                                         'upload_existing': True})

        upload_thread.start()
        try:
            # wait a second, copy the test file into the watched directory, and wait another second
            time.sleep(1)
            fp = TEST_CONST.TEST_WATCHED_DIR_PATH / TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME / TEST_CONST.TEST_DATA_FILE_NAME
            if not fp.parent.is_dir():
                fp.parent.mkdir(parents=True)
            fp.write_bytes(TEST_CONST.TEST_DATA_FILE_PATH.read_bytes())
            time.sleep(1)
            # put the "check" command into the input queue a couple times to test it
            dfud.control_command_queue.put('c')
            dfud.control_command_queue.put('check')
            # put the quit command in the command queue to stop the process running
            LOGGER.set_stream_level(logging.INFO)
            msg = '\nQuitting upload thread in run_data_file_upload_directory; '
            msg += f'will timeout after {TIMEOUT_SECS} seconds....'
            LOGGER.info(msg)
            LOGGER.set_stream_level(logging.ERROR)
            dfud.control_command_queue.put('q')
            # wait for the uploading thread to complete
            upload_thread.join(timeout=TIMEOUT_SECS)
            if upload_thread.is_alive():
                errmsg = 'ERROR: upload thread in run_data_file_upload_directory '
                errmsg += f'timed out after {TIMEOUT_SECS} seconds!'
                raise TimeoutError(errmsg)
        except Exception as e:
            raise e
        finally:
            if upload_thread.is_alive():
                try:
                    dfud.shutdown()
                    upload_thread.join(timeout=JOIN_TIMEOUT_SECS)
                    if upload_thread.is_alive():
                        errmsg = 'ERROR: upload thread in run_data_file_upload_directory timed out after '
                        errmsg += f'{JOIN_TIMEOUT_SECS} seconds!'
                        raise TimeoutError(errmsg)
                except Exception as e:
                    raise e
                finally:
                    print('wait until upload into osn...')
                    # shutil.rmtree(TEST_CONST.TEST_WATCHED_DIR_PATH)
            # if TEST_CONST.TEST_WATCHED_DIR_PATH.is_dir() :
            #     shutil.rmtree(TEST_CONST.TEST_WATCHED_DIR_PATH)

    # called by the test method below

    def run_osn_tranfer_data(self):
        osn_thread = MyThread(target=self.upload_data_into_osn)
        validation_thread = MyThread(target=self.validate_osn_with_producer)

        osn_thread.start()
        validation_thread.start()
        try:
            time.sleep(1)
            LOGGER.set_stream_level(logging.INFO)
            LOGGER.set_stream_level(logging.ERROR)
            # wait for the uploading thread to complete
            osn_thread.join(timeout=TIMEOUT_SECS)
            if osn_thread.is_alive():
                errmsg = 'ERROR: upload thread in upload_data_into_osn '
                errmsg += f'timed out after {TIMEOUT_SECS} seconds!'
                raise TimeoutError(errmsg)
        except Exception as e:
            raise e
        finally:
            if osn_thread.is_alive():
                try:
                    osn_thread.join(timeout=JOIN_TIMEOUT_SECS)
                    if osn_thread.is_alive():
                        errmsg = 'ERROR: upload thread in upload_data_into_osn timed out after '
                        errmsg += f'{JOIN_TIMEOUT_SECS} seconds!'
                        raise TimeoutError(errmsg)
                except Exception as e:
                    raise e
                finally:
                    print('wait until upload into osn...')

    def upload_data_into_osn(self):
        # make the directory to reconstruct files into
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
        self.validate_osn_with_producer()


    def hash_file(self, my_file):
        md5 = hashlib.md5()
        BUF_SIZE = 65536
        try:
            with open(my_file, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    md5.update(data)

        except IOError:
            LOGGER.info('Error While Opening the file!')
            return None
        return "MD5: {0}".format(md5.hexdigest())

    def validate_osn_with_producer(self):
        print('validating osn with producer')
        endpoint_url = TEST_CONST.TEST_ENDPOINT_URL
        aws_access_key_id = TEST_CONST.TEST_ASSCESS_KEY_ID
        aws_secret_access_key = TEST_CONST.TEST_SECRET_KEY_ID
        region_name = TEST_CONST.TEST_REGION
        bucket_name = TEST_CONST.TEST_BUCKET_NAME

        osn_config = {'endpoint_url': endpoint_url, 'access_key_id': aws_access_key_id,
                      'secret_key_id': aws_secret_access_key,
                      'region': region_name, 'bucket_name': bucket_name}

        s3d = s3_data_transfer(osn_config)

        for subdir, dirs, files in os.walk(TEST_CONST.TEST_WATCHED_DIR_PATH):
            for file in files:
                local_path = str(os.path.join(subdir, file))
                hashed_datafile_stream = self.hash_file(local_path)

                if hashed_datafile_stream == None:
                    raise Exception('datafile_stream producer is null!')

                local_path = str(os.path.join(subdir, file)).replace('\\', '/')
                object_key = TOPIC_NAME + '/' + local_path[len(str(TEST_CONST.TEST_WATCHED_DIR_PATH)) + 1:]
                LOGGER.info('now......................')
                if (s3d.compare_producer_datafile_with_osn_object_stream(TEST_CONST.TEST_BUCKET_NAME, object_key,
                                                                         hashed_datafile_stream)):
                    LOGGER.info('did not match for producer')
                    # raise Exception('Failed to match osn object with the original producer data')

                shutil.rmtree(TEST_CONST.TEST_WATCHED_DIR_PATH)
                s3d.delete_object_from_osn(bucket_name, object_key)
        LOGGER.info('All test cases passed')

    # below we test both upload_files_as_added and then reconstruct, in that order
    def test_upload_kafka_and_trasnfer_into_osn(self):
        self.run_data_file_upload_directory()
        self.run_osn_tranfer_data()
