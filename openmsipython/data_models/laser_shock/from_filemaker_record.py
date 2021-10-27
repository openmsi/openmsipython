#imports
import functools
from abc import ABC
from gemd.entity.file_link import FileLink

class FromFileMakerRecordBase(ABC) :
    """
    Base class for specs/runs that will be created from FileMaker Records
    """

    def __init__(self,record,obj) :
        """
        Use information in the given record to populate the given object
        """
        #A list of keys whose values have been recognized and used in reading the record
        self.keys_used = []
        #loop over all the keys/values for the given record and process them one at a time
        for key, value in zip(record.keys(),record.values()) :
            #skip any keys that have already been used
            if key in self.keys_used :
                continue
            #add the name
            elif self.name_key is not None and key==self.name_key :
                obj.name = value
                self.keys_used.append(key)
            #add the tags
            elif key in self.tags_keys :
                obj.tags.append(f'{key.replace(" ","")}::{value.replace(" ","_")}')
                self.keys_used.append(key)
            #add the notes
            elif self.notes_key is not None and key==self.notes_key :
                obj.notes = value
                self.keys_used.append(key)
            #add the file links
            elif key in self.file_links_keys :
                for d in self.file_links_dicts :
                    if ('filename' not in d.keys() or key!=d['filename']) and ('url' not in d.keys() or key!=d['url']) :
                        continue
                    filename=None; url=None
                    if 'filename' in d.keys() :
                        if key==d['filename'] :
                            filename=value
                        elif d['filename'] in record.keys() :
                            filename=record[d['filename']]
                            self.keys_used.append(d['filename'])
                    if 'url' in d.keys() :
                        if key==d['url'] :
                            url=value
                        elif d['url'] in record.keys() :
                            url=record[d['url']]
                            self.keys_used.append(d['url'])
                    if filename is not None or url is not None :
                        if obj.file_links is None :
                            obj.file_links = []
                        obj.file_links.append(FileLink(filename,url))
            #ignore any specified keys
            elif self.ignore_key(key) :
                self.keys_used.append(key)
                continue
            #send any "other" keys to the "add_other_key" function
            elif key in self.other_keys :
                self.add_other_key(key,value,record)
            #if the key hasn't been found anywhere by now, throw an error
            else :
                raise ValueError(f'ERROR: FileMaker record key {key} is not recognized!')
        #make sure all the keys in the record were used in some way
        unused_keys = [k for k in record.keys() if k not in self.keys_used]
        if len(unused_keys)>0 :
            errmsg = f'ERROR: the following keys were not used in creating a {self.__clas__.__name__} object: '
            for k in unused_keys :
                errmsg+=f'{k}, '
            raise ValueError(errmsg[:-2])
        #make sure the record contained all the expected keys and they were processed
        all_keys = [self.name_key,*self.tags_keys,self.notes_key,
                    *self.file_links_keys,
                    *self.other_keys]
        missing_keys = [k for k in all_keys if k is not None and k not in self.keys_used]
        if len(missing_keys)>0 :
            errmsg = 'ERROR: the following expected keys were not found in the record '
            errmsg+= f'used to create a {self.__class__.__name__} object: '
            for k in missing_keys :
                errmsg+=f'{k}, '
            raise ValueError(errmsg[:-2])

    def ignore_key(self,key) :
        """
        Returns "True" for any key that can be ignored, either because 
        they don't contain any useful informationor because they are 
        used in processing other individual keys
        """
        return False

    def add_other_key(self,key,value,record) :
        """
        A function to process a specified key and value uniquely within the child class 
        instead of automatically in this base class

        This function in the base class just throws an error, nothing should call this

        Parameters:
        key    = the key to process
        value  = the value associated with this key in the record
        record = the entire FileMaker record being used to instantiate this object
                 (included in case processing the key requires reading other values in the record)

        Should throw an error if anything goes wrong in processing the key
        
        In child classes it's important to call super().add_other_key(key,value,record) 
        if the key isn't used for that child class
        """
        errmsg = f'ERROR: add_other_key called for key {key} on the base class for a '
        errmsg+= f'{self.__class__.__name__} object! This key should be processed somewhere other than the base class'
        raise NotImplementedError(errmsg)

    @property
    def name_key(self) :
        """
        The FileMaker record key whose value should be used as the name of the object
        (must be implemented in child classes)
        """
        return None

    @property
    def tags_keys(self) :
        """
        A list of keys whose values should be added to the object as tags
        tags will be formatted as 'name::value' where the name is the key with spaces removed
        and value is the value in the record
        """
        return ['recordId','modId']

    @property
    def notes_key(self) :
        """
        The FileMaker record key whose value should be added as "notes" for the run object
        """
        return None

    @property
    @functools.lru_cache(maxsize=10)
    def file_links_keys(self) :
        all_keys = []
        for d in self.file_links_dicts :
            for k in d.keys() :
                all_keys.append(k)
        return all_keys

    @property
    def file_links_dicts(self) :
        """
        The FileMaker record keys whose values should be used to define file_links for the run object
        Each entry in the list should be a dictionary with keys "filename" and "url"
        """
        return []

    @property
    def other_keys(self) :
        """
        A list of keys that need to be processed uniquely by the child class
        when keys in this list are found they are sent back to the "add_other_key" function 
        along with the entire FileMaker record
        """
        return []
