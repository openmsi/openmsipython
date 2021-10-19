#imports
from abc import ABC, abstractmethod
from gemd.entity.util import make_instance
from gemd.entity.source.performed_source import PerformedSource

class RunFromFileMakerRecordBase(ABC) :
    """
    An abstract base class to provide functionality for converting FileMaker records into GEMD "Run" objects
    """

    @property
    @classmethod
    @abstractmethod
    def spec_type(cls) :
        """
        The type of Spec object associated with this type of run object
        (must be implemented in child classes)
        """
        pass

    @property
    @classmethod
    @abstractmethod
    def name_key(cls) :
        """
        The FileMaker record key whose value should be used as the name of the object
        (must be implemented in child classes)
        """
        pass

    @property
    @classmethod
    def notes_key(cls) :
        """
        The FileMaker record key whose value should be added as "notes" for the run object
        """
        return None

    @property
    @classmethod
    def tag_keys(cls) :
        """
        A list of keys whose values should be added to the object as tags
        tags will be formatted as 'name::value' where the name is the key with spaces removed
        and value is the value in the record
        """
        return []

    @property
    @classmethod
    def other_keys(cls) :
        """
        A list of keys that need to be processed uniquely by the child class
        when keys in this list are found they are sent back to the "process_other_key" function 
        along with the entire FileMaker record
        """
        return []

    @classmethod
    def ignore_key(cls,key) :
        """
        Returns "True" for any key that can be ignored, either because 
        they don't contain any useful informationor because they are 
        used in processing other individual keys
        """
        return False

    @classmethod
    def process_other_key(cls,key,value,record,run_obj) :
        """
        A function to process a specified key and value uniquely within the child class 
        instead of automatically in this base class

        Parameters:
        key    = the key to process
        value  = the value associated with this key in the record
        record = the entire FileMaker record being used to instantiate this object
                 (included in case processing the key requires reading other values in the record)
        run_obj = the Run object corresponding to the Spec (so that processing the key can modify the object)

        Should throw an error if anything goes wrong in processing the key
        """
        if cls.other_keys==[] :
            return
        else :
            errmsg = f'ERROR: process_other_key called on a {cls.__name__} object for which '
            errmsg+= f'other_keys={cls.other_keys}. This method must be implemented in the child class!'
            raise NotImplementedError(errmsg)

    @classmethod
    def from_filemaker_record(cls,record) :
        """
        Use the information in a given FileMaker record to populate and return a Run object
        """
        #create an initial object from the spec
        spec = cls.spec_type()
        obj = make_instance(spec)
        #loop over all the keys/values for the given record and process them one at a time
        for key, value in zip(record.keys(),record.values()) :
            #ignore any specified keys
            if cls.ignore_key(key) :
                continue
            #add the name
            elif key==cls.name_key :
                obj.name = value
            #add the notes
            elif cls.notes_key is not None and key==cls.notes_key :
                obj.notes = value
            #search for tags and append them to the list
            elif key in cls.tag_keys :
                obj.tags.append(f'{key.replace(" ","")}::{value.replace(" ","_")}')
            #send any "other" keys to the "process_other_key" function
            elif key in cls.other_keys :
                cls.process_other_key(key,value,record,obj)
            #if the key hasn't been found by now, throw an error
            else :
                raise ValueError(f'ERROR: FileMaker record key {key} is not recognized!')
        #return the completed object
        return obj

class HasSourceRunFromFileMakerRecord(RunFromFileMakerRecordBase) :
    """
    Adds to the base class to process keys for sources 
    """

    @property
    @classmethod
    def performed_by_key(cls) :
        """
        The FileMaker record key whose value should be used as "performed_by" for the source of the object
        """
        return None

    @property
    @classmethod
    def performed_date_key(cls) :
        """
        The FileMaker record key whose value should be used as "performed_date" for the source of the object
        """
        return None

    @property
    @classmethod
    def other_keys(cls) :
        return [*(super(HasSourceRunFromFileMakerRecord,cls).other_keys),
                cls.performed_by_key,
                cls.performed_date_key,
               ]

class MaterialRunFromFileMakerRecord(HasSourceRunFromFileMakerRecord) :
    """
    Class to use for creating MaterialRuns from FileMaker Records
    """

    @classmethod
    def process_other_key(cls,key,value,record,run_obj) :
        #add a Source to the ProcessRun that created this material
        if cls.performed_by_key is not None and key==cls.performed_by_key :
            if run_obj.process.source is None :
                run_obj.process.source = PerformedSource()
            if value!='' :
                run_obj.process.source.performed_by = value
        elif cls.performed_date_key is not None and key==cls.performed_date_key :
            if run_obj.process.source is None :
                run_obj.process.source = PerformedSource()
            if value!='' :
                run_obj.process.source.performed_date = value
        else :
            super(MaterialRunFromFileMakerRecord,cls).process_other_key(cls,key,value,record,run_obj)
