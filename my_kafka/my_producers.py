#Classes that extend Kafka Producers for specific scenarios

#imports
from confluent_kafka import Producer
from ..utilities.misc import populated_kwargs
from ..utilities.config import TUTORIAL_CLUSTER_CONST

#Producer to the tutorial cluster
class TutorialClusterProducer(Producer) :

    def __init__(self,**kwargs) :
        """
        Possible keywork arguments:
        retries : the number of times to retry sending any particular message before erroring out (default is 2)
        """
        kwargs = populated_kwargs(kwargs,{'retries':2,})
        config = {'bootstrap.servers': TUTORIAL_CLUSTER_CONST.SERVER,
                  'sasl.mechanism'   : TUTORIAL_CLUSTER_CONST.SASL_MECHANISM,
                  'security.protocol': TUTORIAL_CLUSTER_CONST.SECURITY_PROTOCOL,
                  'sasl.username'    : TUTORIAL_CLUSTER_CONST.USERNAME,
                  'sasl.password'    : TUTORIAL_CLUSTER_CONST.PASSWORD,
                  'retries'          : kwargs['retries']
                }
        super().__init__(config)
