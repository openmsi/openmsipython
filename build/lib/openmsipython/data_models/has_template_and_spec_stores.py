#imports

class HasTemplateAndSpecStores :
    """
    Base class for any object that has GEMDTemplateStore and GEMDSpecStore 
    objects registered to it when it's initialized
    """

    @property
    def templates(self) :
        return self.__template_store

    @property
    def specs(self) :
        return self.__spec_store

    def __init__(self,*args,templates,specs,**kwargs) :
        #the template store
        self.__template_store = templates
        #the spec store
        self.__spec_store = specs
