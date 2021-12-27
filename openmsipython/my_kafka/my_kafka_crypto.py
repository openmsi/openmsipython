#imports
from kafkacrypto import KafkaProducer, KafkaConsumer, KafkaCrypto

class MyKafkaCrypto :
    """
    A class to own and work with the Producers, Consumers, and other objects needed
    by KafkaCrypto to handle encrypting/decrypting messages and exchanging keys
    """

    @property
    def key_serializer(self) :
        return self._kc.getKeySerializer()
    @property
    def key_deserializer(self) :
        return self._kc.getKeyDeserializer()
    @property
    def value_serializer(self) :
        return self._kc.getValueSerializer()
    @property
    def value_deserializer(self) :
        return self._kc.getValueDeserializer()

    def __init__(self,server_configs,config_file) :
        """
        server_configs = the producer/consumer-agnostic configurations for connecting to the server in question
        config_file    = the path to the config file that should be used to instantiate KafkaCrypto 
        """
        #start up the producer and consumer
        self._kcp = KafkaProducer(server_configs)
        self._kcc = KafkaConsumer(server_configs)
        #initialize the KafkaCrypto object 
        self._kc = KafkaCrypto(None,self._kcp,self._kcc,config_file)