class MyBaseClass(object) :
    """
    A class to use as a sink for eating extra __init__ arguments when using multiple inheritance
    """

    def __init__(self,*args,**kwargs) :
        super().__init__()
