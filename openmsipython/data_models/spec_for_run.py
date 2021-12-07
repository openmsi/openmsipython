#imports
from abc import ABC,abstractmethod

class SpecForRun(ABC) :
    """
    A small base class for dynamically-created Specs
    """

    @property
    @abstractmethod
    def spec_type(self) :
        """
        A property defining the type of GEMD Spec that this SpecForRun creates
        """
        pass

    def __init__(self,*args,**kwargs) :
        #get the kwargs that will be used to create the GEMD Spec
        spec_kwargs = self.get_spec_kwargs()
        #create the GEMD spec
        self.spec = self.spec_type(**spec_kwargs)

    @abstractmethod
    def get_spec_kwargs(self) :
        """
        Returns the dictionary of keyword arguments used to create the GEMD Spec 
        (must be implemented in child classes)
        """
        pass
