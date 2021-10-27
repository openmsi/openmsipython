#imports
from abc import ABC,abstractmethod

class LaserShockSpecForRun(ABC) :
    """
    A small base class to handle keeping dynamically-created Specs unique throughout the entire Laser Shock Lab
    """

    def __init__(self,*args,**kwargs) :
        #want to keep the keyword arguments around to make comparisons between other Specs
        self.kwargs = kwargs
        #get the unique hash based on the arguments to use as a uid
        arghash = self.get_arg_hash()
        #get the kwargs that will be used to create the GEMD Spec
        spec_kwargs = self.get_spec_kwargs()
        #create the GEMD spec
        self.spec = self.spec_type(**spec_kwargs)
        #add the uid for the arghash
        self.spec.add_uid('laser-shock-specs',arghash)

    @property
    @abstractmethod
    def spec_type(self) :
        """
        A property defining the type of GEMD Spec that this LaserShockSpec creates
        """
        pass

    @abstractmethod
    def get_arg_hash(self) :
        """
        Returns the digest of a hash that's unique based on the keyword arguments used to create the Spec 
        (must be implemented in child classes)
        """
        pass

    @abstractmethod
    def get_spec_kwargs(self) :
        """
        Returns the dictionary of keyword arguments used to create the GEMD Spec 
        (must be implemented in child classes)
        """
        pass
