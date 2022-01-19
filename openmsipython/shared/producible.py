#imports
from abc import ABC, abstractmethod

class Producible(ABC) :
    """
    Small utility class for anything that can be Produced as a message to a topic
    """

    @property
    @abstractmethod
    def msg_key(self) :
        """
        The key of the object when it's represented as a message
        This can be something that needs to be serialized still
        Not implemented in base class
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def msg_value(self) :
        """
        The value of the object when it's represented as a message
        This can be something that needs to be serialized still
        Not implemented in base class
        """
        raise NotImplementedError

    @abstractmethod
    def get_log_msg(self,print_every=None) :
        """
        Given some (optional) "print_every" variable, return the string that should be logged for this message
        If "None" is returned nothing will be logged.

        Not implemented in base class
        """
        return None