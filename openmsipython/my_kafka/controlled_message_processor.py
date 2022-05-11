#imports
import time
from abc import ABC, abstractmethod
from ..shared.controlled_process import ControlledProcessMultiThreaded
from .consumer_group import ConsumerGroup

class ControlledMessageProcessor(ControlledProcessMultiThreaded,ConsumerGroup,ABC) :
    """
    Combine a ControlledProcessMultiThreaded and a ConsumerGroup to create a 
    single interface for reading and processing individual messages
    """

    CONSUMER_POLL_TIMEOUT = 0.050
    NO_MESSAGE_WAIT = 0.005 #how long to wait if consumer.get_next_message_value returns None

    def __init__(self,*args,**kwargs) :
        """
        Hang onto the number of messages read and processed
        """
        self.n_msgs_read = 0
        self.n_msgs_processed = 0
        super().__init__(*args,**kwargs)

    def _run_worker(self,lock):
        """
        Handle startup and shutdown of a thread-independent Consumer and 
        serve individual messages to the _process_message function
        """
        #create the Consumer for this thread
        if self.alive :
            consumer = self.get_new_subscribed_consumer()
        #start the loop for while the controlled process is alive
        while self.alive :
            #consume a message from the topic
            msg = consumer.get_next_message_value(ControlledMessageProcessor.CONSUMER_POLL_TIMEOUT)
            if msg is None :
                time.sleep(ControlledMessageProcessor.NO_MESSAGE_WAIT) #wait just a bit to not over-tax things
                continue
            with lock :
                self.n_msgs_read+=1
            #send the message to the _process_message function
            retval = self._process_message(lock,msg)
            if retval :
                with lock :
                    self.n_msgs_processed+=1
        #shut down the Consumer that was created once the process isn't alive anymore
        consumer.close()

    @abstractmethod
    def _process_message(self,lock,msg,*args,**kwargs) :
        """
        Process a single message read from the thread-independent Consumer
        Returns true if processing was successful, and False otherwise
        
        lock = lock across all created child threads (use to enforce thread safety during processing)
        msg  = a single message that was consumed and should be processed by this function

        Not implemented in the base class 
        """
        pass