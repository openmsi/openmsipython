#Classes that extend Kafka Producers for specific scenarios

#imports
from confluent_kafka import Producer
from ..utilities.misc import populated_kwargs
from ..utilities.config import TUTORIAL_CLUSTER_CONST

#Producer to the tutorial cluster
class TutorialClusterProducer(Producer) :

    def __init__(self,**kwargs) :
        """
        Possible keyword arguments:
        batch_size         : the allowed size (in bytes) of each message batch (default=200,000)
        retries            : the number of times to retry sending any particular message before erroring out (default is 2)
        linger_ms          : how long (in ms) each batch of messages should wait to fill with mesages before being sent off (default is 100ms)
        compression_type   : the type of compression algorithm to use for compressing a batch of messages (default: lz4)
        """
        kwargs = populated_kwargs(kwargs,
                                  {'batch_size':200000,
                                   'retries':2,
                                   'linger_ms':100,
                                   'compression_type':'lz4',
                                  })
        config = {'bootstrap.servers'  : TUTORIAL_CLUSTER_CONST.SERVER,
                  'sasl.mechanism'     : TUTORIAL_CLUSTER_CONST.SASL_MECHANISM,
                  'security.protocol'  : TUTORIAL_CLUSTER_CONST.SECURITY_PROTOCOL,
                  'sasl.username'      : TUTORIAL_CLUSTER_CONST.USERNAME,
                  'sasl.password'      : TUTORIAL_CLUSTER_CONST.PASSWORD,
                  'batch.size'         : kwargs['batch_size'],
                  'retries'            : kwargs['retries'],
                  'linger.ms'          : kwargs['linger_ms'],
                  'compression.type'   : kwargs['compression_type'],
                }
        super().__init__(config)
