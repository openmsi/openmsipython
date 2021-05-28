#imports
from config import TEST_CONST
from openmsipython.data_file_io.data_file import DataFile
from openmsipython.data_file_io.data_file_chunk import DataFileChunk
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.utilities.logging import Logger
import unittest, pathlib, logging

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestDataFileChunk(unittest.TestCase) :
    """
    Class for testing DataFileChunk functions (without interacting with the Kafka cluster)
    """

    def setUp(self) :
        #use a DataFile to get a couple chunks to test
        df = DataFile(TEST_CONST.TEST_DATA_FILE_PATH,logger=LOGGER)
        df._build_list_of_file_chunks(RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
        self.test_chunk_1 = df._chunks_to_upload[0]
        self.test_chunk_2 = df._chunks_to_upload[1]
        self.test_chunk_1._populate_with_file_data(logger=LOGGER)
        self.test_chunk_2._populate_with_file_data(logger=LOGGER)

    def test_eq(self) :
        test_chunk_1_copied_no_data = DataFileChunk(self.test_chunk_1.filepath,self.test_chunk_1.filename,self.test_chunk_1.file_hash,self.test_chunk_1.chunk_hash,
                                                    self.test_chunk_1.chunk_offset,self.test_chunk_1.chunk_size,self.test_chunk_1.chunk_i,
                                                    self.test_chunk_1.n_total_chunks)
        test_chunk_2_copied_no_data = DataFileChunk(self.test_chunk_2.filepath,self.test_chunk_2.filename,self.test_chunk_2.file_hash,self.test_chunk_2.chunk_hash,
                                                    self.test_chunk_2.chunk_offset,self.test_chunk_2.chunk_size,self.test_chunk_2.chunk_i,
                                                    self.test_chunk_2.n_total_chunks)
        self.assertNotEqual(self.test_chunk_1,test_chunk_1_copied_no_data)
        self.assertNotEqual(self.test_chunk_2,test_chunk_2_copied_no_data)
        self.assertNotEqual(self.test_chunk_1,self.test_chunk_2)
        self.assertNotEqual(test_chunk_1_copied_no_data,test_chunk_2_copied_no_data)
        test_chunk_1_copied = DataFileChunk(self.test_chunk_1.filepath,self.test_chunk_1.filename,self.test_chunk_1.file_hash,self.test_chunk_1.chunk_hash,
                                            self.test_chunk_1.chunk_offset,self.test_chunk_1.chunk_size,self.test_chunk_1.chunk_i,
                                            self.test_chunk_1.n_total_chunks,self.test_chunk_1.data)
        test_chunk_2_copied = DataFileChunk(self.test_chunk_2.filepath,self.test_chunk_2.filename,self.test_chunk_2.file_hash,self.test_chunk_2.chunk_hash,
                                            self.test_chunk_2.chunk_offset,self.test_chunk_2.chunk_size,self.test_chunk_2.chunk_i,
                                            self.test_chunk_2.n_total_chunks,self.test_chunk_2.data)
        self.assertEqual(self.test_chunk_1,test_chunk_1_copied)
        self.assertEqual(self.test_chunk_2,test_chunk_2_copied)
        self.assertFalse(self.test_chunk_1==2)
        self.assertFalse(self.test_chunk_1=='this is a string, not a DataFileChunk!')
