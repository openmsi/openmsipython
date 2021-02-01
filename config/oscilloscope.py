#imports
from confluent_kafka import Consumer, Producer
import uuid

########################## FILE SCOPE VARIABLES ##########################
oscilloscope_consumer = Consumer({
    'bootstrap.servers': 'pkc-ep9mm.us-east-2.aws.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '5AZU24G7K7AKNSYS',
    'sasl.password': '6H8nMfsoeqJsoBShvtC5GIWHOS6U8La22JDKrWI2BT8wZWKi8qTTHrC3ygFueC2S',
    'group.id': str(uuid.uuid1()),  # this will create a new consumer group on each invocation.
    'auto.offset.reset': 'earliest'
})

oscilloscope_producer = Producer({
    'bootstrap.servers': 'pkc-ep9mm.us-east-2.aws.confluent.cloud:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '5AZU24G7K7AKNSYS',
    'sasl.password': '6H8nMfsoeqJsoBShvtC5GIWHOS6U8La22JDKrWI2BT8wZWKi8qTTHrC3ygFueC2S'
})


########################## CLASS FOR CONSTANT SHARED VARIABLES ##########################
class OscilloscopeConstants :
    @property
    def PRODUCER(self) :
        global oscilloscope_producer
        return oscilloscope_producer #producer to the tutorial_cluster
    @property
    def CONSUMER(self) :
        global oscilloscope_consumer
        return oscilloscope_consumer #consumer from the tutorial_cluster
    @property
    def LECROY_FILE_TOPIC_NAME(self):
        return 'lecroy_files' #name of the topic to which oscilloscope files should be produced in the tutorial_cluster
    
OSC_CONST=OscilloscopeConstants()
