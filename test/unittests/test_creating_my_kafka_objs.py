#imports
import unittest, pathlib, logging
from openmsipython.shared.logging import Logger
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.my_kafka.my_producer import MyProducer
from openmsipython.my_kafka.my_consumer import MyConsumer
from openmsipython.my_kafka.consumer_group import ConsumerGroup
from config import TEST_CONST

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestCreateMyKafkaObjects(unittest.TestCase) :
    """
    Class for testing that objects in openmsipython.my_kafka can 
    be instantiated using default configs
    """

    def test_create_my_producer(self) :
        myproducer = MyProducer.from_file(TEST_CONST.TEST_CONFIG_FILE_PATH,logger=LOGGER)
        self.assertTrue(myproducer is not None)

    def test_create_my_producer_encrypted(self) :
        myproducer = MyProducer.from_file(TEST_CONST.TEST_CONFIG_FILE_PATH_ENCRYPTED,logger=LOGGER)
        self.assertTrue(myproducer is not None)

    def test_create_my_consumer(self) :
        myconsumer = MyConsumer.from_file(TEST_CONST.TEST_CONFIG_FILE_PATH,logger=LOGGER)
        self.assertTrue(myconsumer is not None)
    
    def test_create_my_consumer_encrypted(self) :
        myconsumer = MyConsumer.from_file(TEST_CONST.TEST_CONFIG_FILE_PATH_ENCRYPTED,logger=LOGGER)
        self.assertTrue(myconsumer is not None)

    def test_create_consumer_group(self) :
        cg = ConsumerGroup(TEST_CONST.TEST_CONFIG_FILE_PATH,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,
                           consumer_group_ID='test_create_consumer_group',
                           n_consumers=RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS)
        self.assertTrue(cg is not None)
    
    def test_create_consumer_group_encrypted(self) :
        cg = ConsumerGroup(TEST_CONST.TEST_CONFIG_FILE_PATH_ENCRYPTED,RUN_OPT_CONST.DEFAULT_TOPIC_NAME,
                           consumer_group_ID='test_create_consumer_group_encrypted',
                           n_consumers=RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS)
        self.assertTrue(cg is not None)
