#imports
from config import TEST_CONST
from openmsipython.data_file_io.data_file import UploadDataFile, DownloadDataFile
from openmsipython.data_file_io.data_file_chunk import DataFileChunk
from openmsipython.data_file_io.config import RUN_OPT_CONST, DATA_FILE_HANDLING_CONST
from openmsipython.utilities.logging import Logger
from queue import Queue
from hashlib import sha512
import unittest, pathlib, logging, shutil, filecmp

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestUploadDataFile(unittest.TestCase) :
    """
    Class for testing UploadDataFile functions (without interacting with the Kafka cluster)
    """

    def setUp(self) :
        self.datafile = UploadDataFile(TEST_CONST.TEST_DATA_FILE_PATH,rootdir=TEST_CONST.TEST_DATA_DIR_PATH/TEST_CONST.TEST_DATA_FILE_ROOT_DIR_NAME,logger=LOGGER)

    def test_initial_properties(self) :
        self.assertEqual(self.datafile.filename,TEST_CONST.TEST_DATA_FILE_NAME)
        self.assertTrue(self.datafile.to_upload)
        self.assertFalse(self.datafile.fully_enqueued)
        self.assertTrue(self.datafile.waiting_to_upload)
        self.assertFalse(self.datafile.upload_in_progress)
        self.assertEqual(self.datafile.upload_status_msg,f'{TEST_CONST.TEST_DATA_FILE_NAME} (waiting to be enqueued)')

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
        n_total_chunks = len(self.datafile._chunks_to_upload)
        self.assertFalse(self.datafile.waiting_to_upload)
        self.assertTrue(self.datafile.upload_in_progress)
        self.assertEqual(self.datafile.upload_status_msg,f'{TEST_CONST.TEST_DATA_FILE_NAME} (in progress)')
        self.assertFalse(self.datafile.fully_enqueued)
        self.datafile.add_chunks_to_upload_queue(real_queue,n_threads=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS)
        self.datafile.add_chunks_to_upload_queue(real_queue,n_threads=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS)
        self.datafile.add_chunks_to_upload_queue(real_queue,n_threads=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS)
        self.datafile.add_chunks_to_upload_queue(real_queue)
        self.assertEqual(real_queue.qsize(),n_total_chunks)
        self.assertFalse(self.datafile.waiting_to_upload)
        self.assertFalse(self.datafile.upload_in_progress)
        self.assertEqual(self.datafile.upload_status_msg,f'{TEST_CONST.TEST_DATA_FILE_NAME} (fully enqueued)')
        self.assertTrue(self.datafile.fully_enqueued)
        #and try one more time to add more chunks; this should just return without doing anything
        self.datafile.add_chunks_to_upload_queue(real_queue)

class TestDownloadDataFile(unittest.TestCase) :
    """
    Class for testing DownloadDataFile functions (without interacting with the Kafka cluster)
    """

    def test_write_chunk_to_disk(self) :
        ul_datafile = UploadDataFile(TEST_CONST.TEST_DATA_FILE_PATH,rootdir=TEST_CONST.TEST_DATA_DIR_PATH/TEST_CONST.TEST_DATA_FILE_ROOT_DIR_NAME,logger=LOGGER)
        dl_datafile = None
        TEST_CONST.TEST_RECO_DIR_PATH.mkdir()
        try :
            ul_datafile._build_list_of_file_chunks(RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
            for ic,dfc in enumerate(ul_datafile._chunks_to_upload) :
                dfc._populate_with_file_data(logger=LOGGER)
                subdir_as_path = pathlib.Path('').joinpath(*(pathlib.PurePosixPath(TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME).parts))
                dfc_as_dl = DataFileChunk(subdir_as_path/dfc.filename,dfc.filename,dfc.file_hash,dfc.chunk_hash,dfc.chunk_offset,dfc.chunk_size,
                                          dfc.chunk_i,dfc.n_total_chunks,data=dfc.data)
                dfc_as_dl.rootdir = TEST_CONST.TEST_RECO_DIR_PATH
                if dl_datafile is None :
                    dl_datafile = DownloadDataFile(dfc_as_dl.filepath,logger=LOGGER)
                check = dl_datafile.write_chunk_to_disk(dfc_as_dl)
                #try writing every tenth chunk twice; should return "chunk already added"
                if ic%10==0 :
                    check2 = dl_datafile.write_chunk_to_disk(dfc_as_dl)
                    self.assertEqual(check2,DATA_FILE_HANDLING_CONST.CHUNK_ALREADY_WRITTEN_CODE)
                expected_check_value = DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS
                if ic==len(ul_datafile._chunks_to_upload)-1 :
                    expected_check_value = DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE 
                self.assertEqual(check,expected_check_value)
            if not filecmp.cmp(TEST_CONST.TEST_DATA_FILE_PATH,TEST_CONST.TEST_RECO_DIR_PATH/TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME/dl_datafile.filename,shallow=False) :
                raise RuntimeError('ERROR: files are not the same after reconstruction!')
            (TEST_CONST.TEST_RECO_DIR_PATH/TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME/dl_datafile.filename).unlink()
            dl_datafile._chunk_offsets_downloaded=set()
            hash_missing_some_chunks = sha512()
            for ic,dfc in enumerate(ul_datafile._chunks_to_upload) :
                if ic%3==0 :
                    hash_missing_some_chunks.update(dfc.data)
            hash_missing_some_chunks.digest()
            for ic,dfc in enumerate(ul_datafile._chunks_to_upload) :
                subdir_as_path = pathlib.Path('').joinpath(*(pathlib.PurePosixPath(TEST_CONST.TEST_DATA_FILE_SUB_DIR_NAME).parts))
                dfc_as_dl = DataFileChunk(subdir_as_path/dfc.filename,dfc.filename,dfc.file_hash,dfc.chunk_hash,dfc.chunk_offset,dfc.chunk_size,
                                          dfc.chunk_i,dfc.n_total_chunks,data=dfc.data)
                dfc_as_dl.rootdir = TEST_CONST.TEST_RECO_DIR_PATH
                if ic==len(ul_datafile._chunks_to_upload)-1 :
                    dfc_as_dl.file_hash=hash_missing_some_chunks
                check = dl_datafile.write_chunk_to_disk(dfc_as_dl)
                expected_check_value = DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS
                if ic==len(ul_datafile._chunks_to_upload)-1 :
                    expected_check_value = DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE 
                self.assertEqual(check,expected_check_value)
        except Exception as e :
            raise e
        finally :
            shutil.rmtree(TEST_CONST.TEST_RECO_DIR_PATH)
