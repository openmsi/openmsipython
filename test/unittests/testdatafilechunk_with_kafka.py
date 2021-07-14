#imports
from config import TEST_CONST
from openmsipython.data_file_io.data_file import UploadDataFile
from openmsipython.data_file_io.data_file_chunk import DataFileChunk
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.my_kafka.my_producers import MySerializingProducer
from openmsipython.utilities.logging import Logger
import unittest, pathlib, logging

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestDataFileChunkWithKafka(unittest.TestCase) :
    """
    Class for testing DataFileChunk functions that interact with the Kafka cluster
    """

    def setUp(self) :
        #use a DataFile to get a couple chunks to test
        df = UploadDataFile(TEST_CONST.TEST_DATA_FILE_PATH,rootdir=TEST_CONST.TEST_DATA_FILE_ROOT_DIR_PATH,logger=LOGGER)
        df._build_list_of_file_chunks(RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
        self.test_chunk_1 = df.chunks_to_upload[0]
        self.test_chunk_2 = df.chunks_to_upload[1]
        self.test_chunk_1._populate_with_file_data(logger=LOGGER)
        self.test_chunk_2._populate_with_file_data(logger=LOGGER)

    def test_produce_to_topic(self) :
        producer = MySerializingProducer.from_file(TEST_CONST.TEST_CONFIG_FILE_PATH,logger=LOGGER)
        self.test_chunk_1.produce_to_topic(producer,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,logger=LOGGER)
        producer.flush()
        self.test_chunk_2.produce_to_topic(producer,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,logger=LOGGER)
        producer.flush()

    def test_chunk_of_nonexistent_file(self) :
        nonexistent_file_path = pathlib.Path(__file__).parent / 'never_name_a_file_this.txt'
        self.assertFalse(nonexistent_file_path.is_file())
        chunk_to_fail = DataFileChunk(nonexistent_file_path,nonexistent_file_path.name,self.test_chunk_1.file_hash,self.test_chunk_1.chunk_hash,
                                      self.test_chunk_1.chunk_offset,self.test_chunk_1.chunk_size,self.test_chunk_1.chunk_i,self.test_chunk_1.n_total_chunks)
        LOGGER.set_stream_level(logging.INFO)
        LOGGER.info('\nExpecting two errors below:')
        LOGGER.set_stream_level(logging.ERROR)
        with self.assertRaises(FileNotFoundError) :
            chunk_to_fail._populate_with_file_data(logger=LOGGER)
        producer = MySerializingProducer.from_file(TEST_CONST.TEST_CONFIG_FILE_PATH,logger=LOGGER)
        with self.assertRaises(FileNotFoundError) :
            chunk_to_fail.produce_to_topic(producer,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,logger=LOGGER)
