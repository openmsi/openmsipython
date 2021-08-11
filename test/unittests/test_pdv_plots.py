#imports
import unittest, pathlib, logging, time, shutil
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.utilities.logging import Logger
from openmsipython.pdv.lecroy_file_upload_directory import LecroyFileUploadDirectory
from openmsipython.pdv.pdv_plot_maker import PDVPlotMaker
from config import TEST_CONST
from utilities import MyThread

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)
UPDATE_SECS = 5
TIMEOUT_SECS = 90
TOPIC_NAME = 'test_pdv_plots'

class TestPDVPlots(unittest.TestCase) :
    """
    Class for testing skimming/uploading a Lecroy data file and using its data read into memory to make some plots
    """

    #called by the test method below
    def run_lecroy_file_upload_directory(self) :
        #make the directory to watch
        (TEST_CONST.TEST_WATCHED_DIR_PATH/TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME).mkdir(parents=True)
        #start up the LecroyFileUploadDirectory
        lfud = LecroyFileUploadDirectory(TEST_CONST.TEST_WATCHED_DIR_PATH,rows_to_skip=10000,update_secs=UPDATE_SECS,logger=LOGGER)
        #start upload_files_as_added in a separate thread so we can time it out
        upload_thread = MyThread(target=lfud.upload_files_as_added,
                                 args=(TEST_CONST.TEST_CONFIG_FILE_PATH,TOPIC_NAME),
                                 kwargs={'n_threads':RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                         'chunk_size':RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                         'max_queue_size':RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE,
                                         'new_files_only':True}
                                )
        upload_thread.start()
        try :
            #wait a second, copy the test file into the watched directory, and wait another second
            time.sleep(1)
            (TEST_CONST.TEST_WATCHED_DIR_PATH/TEST_CONST.TEST_LECROY_DATA_FILE_NAME).write_bytes(TEST_CONST.TEST_LECROY_DATA_FILE_PATH.read_bytes())
            time.sleep(1)
            #put the "check" command into the input queue a couple times to test it
            lfud.control_command_queue.put('c')
            lfud.control_command_queue.put('check')
            #put the quit command in the command queue to stop the process running
            LOGGER.set_stream_level(logging.INFO)
            LOGGER.info(f'\nQuitting upload thread in run_lecroy_file_upload_directory; will timeout after {TIMEOUT_SECS} seconds....')
            LOGGER.set_stream_level(logging.ERROR)
            lfud.control_command_queue.put('q')
            #wait for the uploading thread to complete
            upload_thread.join(timeout=TIMEOUT_SECS)
            if upload_thread.is_alive() :
                raise TimeoutError(f'ERROR: upload thread in run_lecroy_file_upload_directory timed out after {TIMEOUT_SECS} seconds!')
        except Exception as e :
            raise e
        finally :
            if upload_thread.is_alive() :
                try :
                    lfud.shutdown()
                    upload_thread.join(timeout=5)
                    if upload_thread.is_alive() :
                        raise TimeoutError('ERROR: upload thread in run_lecroy_file_upload_directory timed out after 5 seconds!')
                except Exception as e :
                    raise e
                finally :
                    shutil.rmtree(TEST_CONST.TEST_WATCHED_DIR_PATH)
            if TEST_CONST.TEST_WATCHED_DIR_PATH.is_dir() :
                shutil.rmtree(TEST_CONST.TEST_WATCHED_DIR_PATH)

    #called by the test method below
    def run_pdv_plot_maker(self) :
        #make the directory to reconstruct files into
        TEST_CONST.TEST_RECO_DIR_PATH.mkdir()
        #start up the PDVPlotMaker
        pdvpm = PDVPlotMaker(TEST_CONST.TEST_RECO_DIR_PATH,
                             'spall',
                             TEST_CONST.TEST_CONFIG_FILE_PATH,
                             TOPIC_NAME,
                             n_threads=RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS,
                             update_secs=UPDATE_SECS,
                             consumer_group_ID='run_pdv_plot_maker',
                             logger=LOGGER,
                            )
        #start make_plots_as_available in a separate thread so we can time it out
        download_thread = MyThread(target=pdvpm.make_plots_as_available)
        download_thread.start()
        try :
            #put the "check" command into the input queue a couple times
            pdvpm.control_command_queue.put('c')
            pdvpm.control_command_queue.put('check')
            #wait for the timeout for the test file to be completely reconstructed or for the reconstructor to stop getting new messages
            current_messages_read = -1
            time_waited = 0
            LOGGER.set_stream_level(logging.INFO)
            LOGGER.info(f'Waiting to read data in skimmed test file from the "{TOPIC_NAME}" topic in run_pdv_plot_maker (will timeout after {TIMEOUT_SECS} seconds)...')
            LOGGER.set_stream_level(logging.ERROR)
            while (TEST_CONST.TEST_LECROY_DATA_FILE_PATH not in pdvpm.processed_filepaths) and current_messages_read<pdvpm.n_msgs_read and time_waited<TIMEOUT_SECS :
                current_messages_read = pdvpm.n_msgs_read
                LOGGER.set_stream_level(logging.INFO)
                LOGGER.info(f'\t{current_messages_read} messages read after waiting {time_waited} seconds....')
                LOGGER.set_stream_level(logging.ERROR)
                time.sleep(5)
                time_waited+=5
            #After timing out, stalling, or completely reconstructing the test file, put the "quit" command into the input queue, which SHOULD stop the method running
            LOGGER.set_stream_level(logging.INFO)
            LOGGER.info(f'Quitting download thread in run_pdv_plot_maker after reading {pdvpm.n_msgs_read} messages; will timeout after 5 seconds....')
            LOGGER.set_stream_level(logging.ERROR)
            pdvpm.control_command_queue.put('q')
            #wait for the download thread to finish
            download_thread.join(timeout=5)
            if download_thread.is_alive() :
                raise TimeoutError('ERROR: download thread in run_pdv_plot_maker timed out after 5 seconds!')
            #make sure the plot image file exists
            self.assertTrue((TEST_CONST.TEST_RECO_DIR_PATH/f'pdv_spall_plots_{TEST_CONST.TEST_LECROY_DATA_FILE_NAME.rstrip(".txt")}.png').is_file())
        except Exception as e :
            raise e
        finally :
            if download_thread.is_alive() :
                try :
                    pdvpm.control_command_queue.put('q')
                    download_thread.join(timeout=5)
                    if download_thread.is_alive() :
                        raise TimeoutError('ERROR: download thread in run_pdv_plot_maker timed out after 5 seconds!')
                except Exception as e :
                    raise e
                finally :
                    shutil.rmtree(TEST_CONST.TEST_RECO_DIR_PATH)
            if TEST_CONST.TEST_RECO_DIR_PATH.is_dir() :
                shutil.rmtree(TEST_CONST.TEST_RECO_DIR_PATH)

    def test_making_pdv_plots_kafka(self) :
        self.run_lecroy_file_upload_directory()
        self.run_pdv_plot_maker()