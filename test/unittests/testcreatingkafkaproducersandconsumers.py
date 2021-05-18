#imports
from openmsipython.my_kafka.my_producers import MyProducer, MySerializingProducer
from openmsipython.my_kafka.my_consumers import MyConsumer, MyDeserializingConsumer
from openmsipython.utilities.logging import Logger
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.utilities.argument_parsing import CONFIG_FILE_DIR, CONFIG_FILE_EXT
import unittest, pathlib, logging

#constants
TEST_CONFIG_FILE_PATH = (CONFIG_FILE_DIR / f'{RUN_OPT_CONST.DEFAULT_CONFIG_FILE}{CONFIG_FILE_EXT}').resolve()
TEST_CONFIG_FILE_PATH_NO_SERIALIZATION = (CONFIG_FILE_DIR / 'test_no_serialization.config').resolve()
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestCreatingKafkaProducersAndConsumers(unittest.TestCase) :
    """
    Class for testing that objects in openmsipython.my_kafka.my_[producers/consumers].py can be instantiated using default configs
    """

    def test_create_my_producer(self) :
        myproducer = MyProducer.from_file(TEST_CONFIG_FILE_PATH_NO_SERIALIZATION,logger=LOGGER)
        myproducer = myproducer

    def test_create_my_serializing_producer(self) :
        myserializingproducer = MySerializingProducer.from_file(TEST_CONFIG_FILE_PATH,logger=LOGGER)
        myserializingproducer = myserializingproducer

    def test_create_my_consumer(self) :
        myconsumer = MyConsumer.from_file(TEST_CONFIG_FILE_PATH_NO_SERIALIZATION,logger=LOGGER)
        myconsumer = myconsumer

    def test_create_my_deserializing_consumer(self) :
        mydeserializingconsumer = MyDeserializingConsumer.from_file(TEST_CONFIG_FILE_PATH,logger=LOGGER)
        mydeserializingconsumer = mydeserializingconsumer
