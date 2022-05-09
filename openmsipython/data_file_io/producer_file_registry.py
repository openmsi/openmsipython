#imports
import pathlib, re, datetime
from typing import Set
from dataclasses import dataclass
from ..shared.dataclass_table import DataclassTable

@dataclass
class RegistryLineInProgress :
    filename : str
    filepath : pathlib.Path
    n_chunks : int
    n_chunks_delivered : int
    n_chunks_to_send : int
    started_at : datetime.datetime
    chunks_delivered : Set[int]
    chunks_to_send : Set[int]

@dataclass
class RegistryLineCompleted :
    filename : str
    filepath : pathlib.Path
    n_chunks : int
    started_at : datetime.datetime
    completed_at : datetime.datetime

class ProducerFileRegistry() :
    """
    A class to manage two atomic csv files listing which portions 
    of which files have been uploaded to a particular topic
    """

    @property
    def REGISTRY_EXCLUDE_REGEX(self) :
        #matches everything except a few specific files that are part of this ProducerFileRegistry
        return re.compile(r'^((?!(REGISTRY_(files_to_upload_to_|files_fully_uploaded_to_).*.csv))).*$')

    def __init__(self,dirpath,topic_name,*args,**kwargs) :
        """
        dirpath    = path to the directory that should contain the csv file
        topic_name = the name of the topic that will be produced to (used in the filename)
        """
        #A table to list the files currently in progress
        in_prog_filepath = dirpath / f'REGISTRY_files_to_upload_to_{topic_name}.csv'
        self.__in_prog = DataclassTable(dataclass_type=RegistryLineInProgress,*args,
                                        filepath=in_prog_filepath,**kwargs)
        #A table to list the files that have been completely produced
        completed_filepath = dirpath / f'REGISTRY_files_fully_uploaded_to_{topic_name}.csv'
        self.__completed = DataclassTable(dataclass_type=RegistryLineCompleted,*args,
                                          filepath=completed_filepath,**kwargs)

    def get_incomplete_filepaths_and_chunks(self) :
        """
        Generate tuples of (filepath, chunks to upload) for each file that has not yet been completely uploaded
        """
        for obj_address in self.__in_prog.obj_addresses :
            yield self.__in_prog.get_entry_attrs(obj_address,'filepath','chunks_to_send')

    def get_completed_filepaths(self) :
        """
        Generate filepaths for each file that has been completely uploaded
        """
        for obj_address in self.__completed.obj_addresses :
            yield self.__completed.get_entry_attrs(obj_address,'filepath')

    def register_chunk(self,filename,filepath,n_total_chunks,chunk_i) :
        """
        Register a chunk as having been successfully produced
        Returns True if all chunks for the file have been produced
        """
        pass
