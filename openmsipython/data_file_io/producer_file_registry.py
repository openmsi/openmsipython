#imports
import pathlib
from dataclasses import dataclass
from ..shared.dataclass_table import DataclassTable

@dataclass
class RegistryLine :
    filename : str
    filepath : pathlib.Path
    n_chunks : int
    n_chunks_delivered : int
    chunks_delivered : str
    n_chunks_to_send : int
    chunks_to_send : str

class ProducerFileRegistry(DataclassTable) :
    """
    A class to manage an atomic csv file listing which portions 
    of which files have been uploaded to a particular topic
    """

    def __init__(self,dirpath,topic_name,*args,**kwargs) :
        """
        dirpath    = path to the directory that should contain the csv file
        topic_name = the name of the topic that will be produced to (used in the filename)
        """
        filepath = dirpath / f'files_uploaded_to_{topic_name}.csv'
        super().__init__(dataclass_type=RegistryLine,*args,filepath=filepath,key_attr_name='filepath',**kwargs)
