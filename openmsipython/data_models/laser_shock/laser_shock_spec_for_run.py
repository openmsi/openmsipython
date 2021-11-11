#imports
from abc import ABC,abstractmethod

class LaserShockSpecForRun(ABC) :
    """
    A small base class to handle keeping dynamically-created Specs unique throughout the entire Laser Shock Lab
    """

    def __init__(self,*args,**kwargs) :
        #get the kwargs that will be used to create the GEMD Spec
        spec_kwargs = self.get_spec_kwargs()
        #create the GEMD spec
        self.spec = self.spec_type(**spec_kwargs)

    @property
    @abstractmethod
    def spec_type(self) :
        """
        A property defining the type of GEMD Spec that this LaserShockSpec creates
        """
        pass

    @abstractmethod
    def get_spec_kwargs(self) :
        """
        Returns the dictionary of keyword arguments used to create the GEMD Spec 
        (must be implemented in child classes)
        """
        pass
