#Classes that extend Kafka Consumers for specific scenarios

#imports
from confluent_kafka import Consumer
from ..utilities.misc import populated_kwargs
from ..utilities.config import TUTORIAL_CLUSTER_CONST
import uuid

#Producer to the tutorial cluster
class TutorialClusterConsumer(Consumer) :

    def __init__(self,**kwargs) :
        """
        Possible keyword arguments:
        group_id          = ID for the group that this consumer should belong to
        auto_offset_reset = argument for auto.offset.reset for this consumer
        """
        kwargs = populated_kwargs(kwargs,
                                  {'group_id':str(uuid.uuid1()), # this will create a new consumer group on each invocation by default
                                   'auto_offset_reset':'earliest'
                                  })
        config = {'bootstrap.servers': TUTORIAL_CLUSTER_CONST.SERVER,
                  'sasl.mechanism'   : TUTORIAL_CLUSTER_CONST.SASL_MECHANISM,
                  'security.protocol': TUTORIAL_CLUSTER_CONST.SECURITY_PROTOCOL,
                  'sasl.username'    : TUTORIAL_CLUSTER_CONST.USERNAME,
                  'sasl.password'    : TUTORIAL_CLUSTER_CONST.PASSWORD,
                  'group.id'         : kwargs['group_id'],  
                  'auto.offset.reset': kwargs['auto_offset_reset']
                }
        super().__init__(config)
