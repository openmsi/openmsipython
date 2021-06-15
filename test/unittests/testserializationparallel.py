#imports
from config import TEST_CONST
from openmsipython.my_kafka.serialization import DataFileChunkSerializer, DataFileChunkDeserializer
from openmsipython.data_file_io.data_file import UploadDataFile
from openmsipython.data_file_io.config import RUN_OPT_CONST
from openmsipython.utilities.logging import Logger
from confluent_kafka.error import SerializationError
import unittest, pathlib, logging

#constants
LOGGER = Logger(pathlib.Path(__file__).name.split('.')[0],logging.ERROR)

class TestSerialization(unittest.TestCase) :
    """
    Class for testing classes in openmsipython.my_kafka.serialization
    """

    def setUp(self) :
        #make the dictionary of reference serialized binaries from the existing reference files
        self.test_chunk_binaries = {}
        for tcfp in TEST_CONST.TEST_DATA_DIR_PATH.glob(f'{TEST_CONST.TEST_DATA_FILE_NAME.split(".")[0]}_test_chunk_*.bin') :
            with open(tcfp,'rb') as fp :
                self.test_chunk_binaries[tcfp.name.split('.')[0].split('_')[-1]] = fp.read()
        if len(self.test_chunk_binaries)<1 :
            msg = 'ERROR: could not find any binary DataFileChunk test files to use as references for TestSerialization '
            msg+= f'in {TEST_CONST.TEST_DATA_DIR_PATH}!'
            raise RuntimeError(msg)
        #make the dictionary of reference DataFileChunk objects
        data_file = UploadDataFile(TEST_CONST.TEST_DATA_FILE_PATH,logger=LOGGER)
        data_file._build_list_of_file_chunks(RUN_OPT_CONST.DEFAULT_CHUNK_SIZE)
        self.test_chunk_objects = {}
        for chunk_i in self.test_chunk_binaries.keys() :
            data_file._chunks_to_upload[int(chunk_i)]._populate_with_file_data(LOGGER)
            self.test_chunk_objects[chunk_i] = data_file._chunks_to_upload[int(chunk_i)]

    def test_data_file_chunk_serializer(self) :
        dfcs = DataFileChunkSerializer()
        self.assertIsNone(dfcs(None)) #required by Kafka
        with self.assertRaises(SerializationError) :
            dfcs('This is a string, not a DataFileChunk!')
        for chunk_i in self.test_chunk_binaries.keys() :
            self.assertEqual(dfcs(self.test_chunk_objects[chunk_i]),self.test_chunk_binaries[chunk_i])

    def test_data_file_chunk_deserializer(self) :
        dfcds = DataFileChunkDeserializer()
        self.assertIsNone(dfcds(None)) #required by Kafka
        with self.assertRaises(SerializationError) :
            dfcds('This is a string, not an array of bytes!')
        for chunk_i in self.test_chunk_binaries.keys() :
            self.assertEqual(self.test_chunk_objects[chunk_i],dfcds(self.test_chunk_binaries[chunk_i]))
