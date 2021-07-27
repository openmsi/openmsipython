#imports
import unittest, pathlib, logging
from queue import Queue
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.utilities.logging import Logger
from openmsipython.data_file_io.upload_data_file import UploadDataFile
from config import TEST_CONST

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestUploadDataFile(unittest.TestCase) :
    """
    Class for testing UploadDataFile functions
    """

    def setUp(self) :
        self.datafile = UploadDataFile(TEST_CONST.TEST_DATA_FILE_PATH,rootdir=TEST_CONST.TEST_DATA_FILE_ROOT_DIR_PATH,logger=LOGGER)

    def test_upload_whole_file_kafka(self) :
        #just need to make sure this function runs without throwing any errors
        self.datafile.upload_whole_file(TEST_CONST.TEST_CONFIG_FILE_PATH,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,
                                        n_threads=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                        chunk_size=RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)

    def test_initial_properties(self) :
        self.assertEqual(self.datafile.filename,TEST_CONST.TEST_DATA_FILE_NAME)
        self.assertTrue(self.datafile.to_upload)
        self.assertFalse(self.datafile.fully_enqueued)
        self.assertTrue(self.datafile.waiting_to_upload)
        self.assertFalse(self.datafile.upload_in_progress)
        self.assertEqual(self.datafile.upload_status_msg,f'{TEST_CONST.TEST_DATA_FILE_PATH.relative_to(self.datafile.rootdir)} (waiting to be enqueued)')

    def test_add_chunks_to_upload_queue(self) :
        #adding to a full Queue should do nothing
        full_queue = Queue(maxsize=3)
        full_queue.put('I am going to')
        full_queue.put('fill this Queue completely')
        full_queue.put('so giving it to add_chunks_to_upload_queue should not change it!')
        self.datafile.add_chunks_to_upload_queue(full_queue)
        self.assertEqual(full_queue.get(),'I am going to')
        self.assertEqual(full_queue.get(),'fill this Queue completely')
        self.assertEqual(full_queue.get(),'so giving it to add_chunks_to_upload_queue should not change it!')
        self.assertEqual(full_queue.qsize(),0)
        #add 0 chunks to just make the full list, then a few chunks, and then the rest
        real_queue = Queue()
        self.datafile.add_chunks_to_upload_queue(real_queue,n_threads=0)
        n_total_chunks = len(self.datafile.chunks_to_upload)
        self.assertFalse(self.datafile.waiting_to_upload)
        self.assertTrue(self.datafile.upload_in_progress)
        self.assertEqual(self.datafile.upload_status_msg,f'{TEST_CONST.TEST_DATA_FILE_PATH.relative_to(self.datafile.rootdir)} (in progress)')
        self.assertFalse(self.datafile.fully_enqueued)
        self.datafile.add_chunks_to_upload_queue(real_queue,n_threads=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS)
        self.datafile.add_chunks_to_upload_queue(real_queue,n_threads=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS)
        self.datafile.add_chunks_to_upload_queue(real_queue,n_threads=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS)
        self.datafile.add_chunks_to_upload_queue(real_queue)
        self.assertEqual(real_queue.qsize(),n_total_chunks)
        self.assertFalse(self.datafile.waiting_to_upload)
        self.assertFalse(self.datafile.upload_in_progress)
        self.assertEqual(self.datafile.upload_status_msg,f'{TEST_CONST.TEST_DATA_FILE_PATH.relative_to(self.datafile.rootdir)} (fully enqueued)')
        self.assertTrue(self.datafile.fully_enqueued)
        #and try one more time to add more chunks; this should just return without doing anything
        self.datafile.add_chunks_to_upload_queue(real_queue)
