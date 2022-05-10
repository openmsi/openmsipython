#imports
import pathlib, re, datetime
from typing import Set
from dataclasses import dataclass
from ..shared.dataclass_table import DataclassTable
from ..shared.logging import LogOwner

@dataclass
class RegistryLineInProgress :
    filename : str
    filepath : pathlib.Path
    n_chunks : int
    n_chunks_delivered : int
    n_chunks_to_send : int
    started : datetime.datetime
    chunks_delivered : Set[int]
    chunks_to_send : Set[int]

@dataclass
class RegistryLineCompleted :
    filename : str
    filepath : pathlib.Path
    n_chunks : int
    started : datetime.datetime
    completed : datetime.datetime

class ProducerFileRegistry(LogOwner) :
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
        super().__init__(*args,**kwargs)
        #A table to list the files currently in progress
        in_prog_filepath = dirpath / f'REGISTRY_files_to_upload_to_{topic_name}.csv'
        self.__in_prog = DataclassTable(dataclass_type=RegistryLineInProgress,filepath=in_prog_filepath,
                                        logger=self.logger)
        #A table to list the files that have been completely produced
        completed_filepath = dirpath / f'REGISTRY_files_fully_uploaded_to_{topic_name}.csv'
        self.__completed = DataclassTable(dataclass_type=RegistryLineCompleted,filepath=completed_filepath,
                                          logger=self.logger)

    def get_incomplete_filepaths_and_chunks(self) :
        """
        Generate tuples of (filepath, chunks to upload) for each file that has not yet been completely uploaded
        """
        for obj_address in self.__in_prog.obj_addresses :
            attr_dict = self.__in_prog.get_entry_attrs(obj_address,'filepath','chunks_to_send')
            if len(attr_dict['chunks_to_send'])>0 :
                yield attr_dict['filepath'],attr_dict['chunks_to_send']

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
        #get a dictionary of the existing object addresses keyed by their filepaths
        existing_obj_addresses = self.__in_prog.obj_addresses_by_key_attr('filepath')
        #if the file is already recognized as in progress
        if filepath in existing_obj_addresses.keys() :
            #make sure there's only one object with this filepath
            if len(existing_obj_addresses[filepath])!=1 :
                errmsg = f'ERROR: found {len(existing_obj_addresses[filepath])} files in the producer registry '
                errmsg+= f'for filepath {filepath}'
                self.logger.error(errmsg,RuntimeError)
            #get its current state
            current_attrs = self.__in_prog.get_entry_attrs(existing_obj_addresses[filepath],
                                                           'n_chunks','n_chunks_delivered','n_chunks_to_send',
                                                           'chunks_delivered','chunks_to_send')
            #make sure the total numbers of chunks match
            if current_attrs['n_chunks']!=n_total_chunks :
                errmsg = f'ERROR: {filepath} in {self.__class__.__name__} is listed as having '
                errmsg+= f'{current_attrs["n_chunks"]} total chunks, but a callback for this file '
                errmsg+= f'lists {n_total_chunks} chunks!'
                self.logger.error(errmsg,RuntimeError)
            #add this chunk index to the set of delivered chunk indices
            new_chunks_delivered = current_attrs['chunks_delivered']
            new_chunks_delivered.add(chunk_i)
            #remove this chunk index from the set of chunk indices to send
            new_chunks_to_send = current_attrs['chunks_to_send']
            #because of "at least once" the chunk index might not be listed
            try :
                new_chunks_to_send.remove(chunk_i)
            except KeyError :
                pass
            # if there are no more chunks to send and all chunks have been delivered, 
            # move this file from "in progress" to "completed" and force-dump the files
            if len(new_chunks_to_send)==0 and len(new_chunks_delivered)==n_total_chunks :
                started = self.__in_prog.get_entry_attrs(existing_obj_addresses[filepath],'started')
                completed_entry = RegistryLineCompleted(filename,filepath,n_total_chunks,
                                                        started,datetime.datetime.now())
                self.__completed.add_entries(completed_entry)
                self.__completed.dump_to_file()
                self.__in_prog.remove_entries(existing_obj_addresses[filepath])
                self.__in_prog.dump_to_file()
                return True
            #otherwise just update the object in the "in progress" table
            else :
                new_attrs = {
                    'n_chunks_delivered':len(new_chunks_delivered),
                    'n_chunks_to_send':len(new_chunks_to_send),
                    'chunks_delivered':new_chunks_delivered,
                    'chunks_to_send':new_chunks_to_send,
                    }
                self.__in_prog.set_entry_attrs(existing_obj_addresses[filepath],**new_attrs)
                return False
        #otherwise it's a new file to add to "in_progress"
        else :
            to_deliver = set([])
            for ic in range(1,n_total_chunks+1) :
                if ic!=chunk_i :
                    to_deliver.add(ic)
            in_prog_entry = RegistryLineInProgress(filename,filepath,n_total_chunks,
                                                   1,n_total_chunks-1,datetime.datetime.now(),
                                                   set([chunk_i]),to_deliver)
            self.__in_prog.add_entries(in_prog_entry)
            return False
