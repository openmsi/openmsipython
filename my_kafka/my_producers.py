#Classes that extend Kafka Producers for specific scenarios

#imports
from confluent_kafka import Producer
from ..utilities.config import TUTORIAL_CLUSTER_CONST

#Producer to the tutorial cluster
class TutorialClusterProducer(Producer) :

    def __init__(self) :
        config = {'bootstrap.servers': TUTORIAL_CLUSTER_CONST.SERVER,
                  'sasl.mechanism'   : TUTORIAL_CLUSTER_CONST.SASL_MECHANISM,
                  'security.protocol': TUTORIAL_CLUSTER_CONST.SECURITY_PROTOCOL,
                  'sasl.username'    : TUTORIAL_CLUSTER_CONST.USERNAME,
                  'sasl.password'    : TUTORIAL_CLUSTER_CONST.PASSWORD
                }
        super().__init__(config)
