#imports
import unittest
from confluent_kafka.serialization import DoubleSerializer, IntegerSerializer, StringSerializer
from confluent_kafka.serialization import DoubleDeserializer, IntegerDeserializer, StringDeserializer
from openmsipython.my_kafka.utilities import get_transformed_configs, get_replaced_configs
from openmsipython.my_kafka.serialization import DataFileChunkSerializer, DataFileChunkDeserializer

class ReplacementDummyClass :
    """
    A dummy class to use to test the replacement
    """

    def __init__(self) :
        pass

class TestMyKafkaUtilities(unittest.TestCase) :
    """
    Class for testing functions in openmsipython.my_kafka.utilities
    """

    def test_get_transformed_configs(self) :
        test_config_dict = {'parameter_A':'a',
                            'parameter_1':1,
                            'parameter_dummy_class':'ReplacementDummyClass',
                            'parameter_None':None,
                        }
        ref_config_dict = test_config_dict.copy()
        names_classes = {'ReplacementDummyClass':ReplacementDummyClass}
        test_config_dict = get_transformed_configs(test_config_dict,names_classes)
        for k in ref_config_dict.keys() :
            self.assertTrue(k in test_config_dict.keys())
        for k in test_config_dict.keys() :
            self.assertTrue(k in ref_config_dict.keys())
            if k=='parameter_dummy_class' :
                self.assertTrue(isinstance(test_config_dict[k],ReplacementDummyClass))
            else :
                self.assertEqual(test_config_dict[k],ref_config_dict[k])
        with self.assertRaises(AttributeError) :
            _ = get_transformed_configs(None,None)
        with self.assertRaises(AttributeError) :
            _ = get_transformed_configs(test_config_dict,[1,2,3])
        with self.assertRaises(AttributeError) :
            _ = get_transformed_configs('this is a string not a dict!',names_classes)

    def test_get_replaced_configs(self) :
        test_config_dict = {'par_1': 'DoubleSerializer',
                            'par_2': 'IntegerSerializer',
                            'par_3': 'StringSerializer',
                            'par_4': 'DataFileChunkSerializer',
                            'par_5': 'DoubleDeserializer',
                            'par_6': 'IntegerDeserializer',
                            'par_7': 'StringDeserializer',
                            'par_8': 'DataFileChunkDeserializer',
                        }
        ref_classes_dict = {'par_1': DoubleSerializer, 
                            'par_2': IntegerSerializer, 
                            'par_3': StringSerializer, 
                            'par_4': DataFileChunkSerializer, 
                            'par_5': DoubleDeserializer, 
                            'par_6': IntegerDeserializer, 
                            'par_7': StringDeserializer, 
                            'par_8': DataFileChunkDeserializer, 
                        }
        test_config_dict_1 = test_config_dict.copy()
        test_config_dict_1 = get_replaced_configs(test_config_dict_1,'serialization')
        for k in test_config_dict_1 :
            if k in ['par_1','par_2','par_3','par_4'] :
                self.assertTrue(isinstance(test_config_dict_1[k],ref_classes_dict[k]))
            else :
                self.assertEqual(test_config_dict_1[k],test_config_dict[k])
        test_config_dict_2 = test_config_dict.copy()
        test_config_dict_2 = get_replaced_configs(test_config_dict_2,'deserialization')
        for k in test_config_dict_2 :
            if k in ['par_5','par_6','par_7','par_8'] :
                self.assertTrue(isinstance(test_config_dict_2[k],ref_classes_dict[k]))
            else :
                self.assertEqual(test_config_dict_2[k],test_config_dict[k])
        with self.assertRaises(AttributeError) :
            _ = get_transformed_configs(None,None)
        with self.assertRaises(AttributeError) :
            _ = get_transformed_configs(test_config_dict,'never make this a recognized parameter group name')
