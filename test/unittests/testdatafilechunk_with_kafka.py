#imports
from config import TEST_CONST
from openmsipython.data_file_io.data_file import DataFile
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
        df = DataFile(TEST_CONST.TEST_DATA_FILE_PATH,logger=LOGGER)
        df._build_list_of_file_chunks(RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
        self.test_chunk_1 = df._chunks_to_upload[0]
        self.test_chunk_2 = df._chunks_to_upload[1]
        self.test_chunk_1._populate_with_file_data(logger=LOGGER)
        self.test_chunk_2._populate_with_file_data(logger=LOGGER)

    def test_produce_to_topic(self) :
        producer = MySerializingProducer.from_file(TEST_CONST.TEST_CONFIG_FILE_PATH,logger=LOGGER)
        self.test_chunk_1.produce_to_topic(producer,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,logger=LOGGER)
        producer.flush()
        self.test_chunk_2.produce_to_topic(producer,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,logger=LOGGER)
        producer.flush()
