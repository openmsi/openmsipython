#imports
import functools
from abc import ABC, abstractmethod
from gemd.entity.util import make_instance
from gemd.entity.file_link import FileLink
from gemd.entity.source.performed_source import PerformedSource
from gemd.entity.attribute import Property
from gemd.entity.object import MeasurementSpec, MeasurementRun

class RunFromFileMakerRecordBase(ABC) :
    """
    An abstract base class to provide functionality for using FileMaker records 
    to create and/or link GEMD "Spec" and Run" objects
    """

    def __init__(self,record,specs=None) :
        """
        Use the information in a given FileMaker record to populate this Run object
        """
        #A list of keys whose values have been recognized and used in creating this Run
        self.keys_used = []
        #figure out the Spec for this Run
        spec = self.get_spec(record,specs)
        #create an initial object from the spec
        self.__run = make_instance(spec)
        #set the name of the Run from the Spec if there is no key defining the name
        if self.name_key is None :
            self.__run.name=self.__spec.name
        #loop over all the keys/values for the given record and process them one at a time
        for key, value in zip(record.keys(),record.values()) :
            #skip any keys that have already been used
            if key in self.keys_used :
                continue
            #add the name
            elif self.name_key is not None and key==self.name_key :
                self.__run.name = value
                self.keys_used.append(key)
            #add the tags
            elif key in self.tags_keys :
                self.__run.tags.append(f'{key.replace(" ","")}::{value.replace(" ","_")}')
                self.keys_used.append(key)
            #add the notes
            elif self.notes_key is not None and key==self.notes_key :
                self.__run.notes = value
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
                        if self.__run.file_links is None :
                            self.__run.file_links = []
                        self.__run.file_links.append(FileLink(filename,url))
            #ignore any specified keys
            elif self.ignore_key(key) :
                self.keys_used.append(key)
                continue
            #send any "other" keys to the "process_other_key" function
            elif key in self.other_keys :
                self.process_other_key(key,value,record)
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
        missing_keys = [k for k in all_keys if k not in self.keys_used]
        if len(missing_keys)>0 :
            errmsg = 'ERROR: the following expected keys were not found in the record '
            errmsg+= f'used to create a {self.__clas__.__name__} object: '
            for k in missing_keys :
                errmsg+=f'{k}, '
            raise ValueError(errmsg[:-2])

    @property
    def run(self) :
        return self.__run

    @abstractmethod
    def get_spec(self,record,specs) :
        """
        A function to return the Spec for this Run given a FileMaker record
        and some existing specs that might be reused
        (must be implemented in child classes)
        """
        pass

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
        when keys in this list are found they are sent back to the "process_other_key" function 
        along with the entire FileMaker record
        """
        return []

    def ignore_key(self,key) :
        """
        Returns "True" for any key that can be ignored, either because 
        they don't contain any useful informationor because they are 
        used in processing other individual keys
        """
        return False

    def process_other_key(self,key,value,record) :
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
        
        In child classes it's important to call super().process_other_key(key,value,record) 
        if the key isn't used for that child class
        """
        errmsg = f'ERROR: process_other_key called for key {key} on the base class for a '
        errmsg+= f'{self.__class__.__name__} object! This key should be processed somewhere other than the base class'
        raise NotImplementedError(errmsg)

class HasSourceRunFromFileMakerRecord(RunFromFileMakerRecordBase) :
    """
    Adds to the base class to process keys for sources 
    Exactly what the source should be added to depends on the type of Objects being created
    """

    @property
    def performed_by_key(self) :
        """
        The FileMaker record key whose value should be used as "performed_by" for the source of the object
        """
        return None

    @property
    def performed_date_key(self) :
        """
        The FileMaker record key whose value should be used as "performed_date" for the source of the object
        """
        return None

    @property
    def other_keys(self) :
        return [*super().other_keys,
                self.performed_by_key,
                self.performed_date_key,
               ]

class MaterialRunFromFileMakerRecord(HasSourceRunFromFileMakerRecord) :
    """
    Class to use for creating Material(Spec/Run) objects from FileMaker Records
    """

    @property
    def measured_property_dict(self) :
        """
        A dictionary whose keys are FileMaker record keys corresponding to single  
        properties of the material that may have been measured. Values for each 
        key are themselves dictionaries, used to add minimal MeasurementRun objects 
        (with accompanying Specs) to this material. 

        If values in the record for any given keys are "''", the MeasurementRun is not added
        to the material, but the key is still marked as consumed.

        The allowed keys and values for each entry's characteristic dictionary are:
        valuetype:   the BaseValue object type for the Property that's measured
        datatype:    datatype to which the value from the FileMaker record should be cast 
                     when added to the Value of the Property
        template:    the AttributeTemplate defining the Property that's measured
        """
        return {}

    @property
    def other_keys(self) :
        return [*super().other_keys,
                *self.measured_property_dict.keys(),
               ]

    def process_other_key(self,key,value,record) :
        #add a PerformedSource to the ProcessRun that created this material
        if self.performed_by_key is not None and key==self.performed_by_key :
            if self.run.process.source is None :
                self.run.process.source = PerformedSource()
            if value!='' :
                self.run.process.source.performed_by = value
            self.keys_used.append(key)
        elif self.performed_date_key is not None and key==self.performed_date_key :
            if self.run.process.source is None :
                self.run.process.source = PerformedSource()
            if value!='' :
                self.run.process.source.performed_date = value
            self.keys_used.append(key)
        #add measured properties (if any of them are given) by creating MeasurementRuns linked to this MaterialRun
        elif key in self.measured_property_dict.keys() :
            self.keys_used.append(key)
            if value=='' :
                return
            name = key.replace(' ','')
            d = self.measured_property_dict[key]
            meas = MeasurementRun(name=name,material=self)
            meas.spec = MeasurementSpec(name=name)
            val = value
            if 'datatype' in d.keys() :
                val = d['datatype'](val)
            temp = None
            if 'template' in d.keys() :
                temp = d['template']
            meas.properties.append(Property(name=name,
                                            value=d['valuetype'](val,origin='measured'),
                                            template=temp))
        else :
            super().process_other_key(key,value,record)

class MeasurementRunFromFileMakerRecord(HasSourceRunFromFileMakerRecord) :
    """
    Class to use for creating Measurement(Spec/Run)s based on FileMaker records
    """

    def process_other_key(self,key,value,record) :
        #add a PerformedSource for this measurement
        if self.performed_by_key is not None and key==self.performed_by_key :
            if self.run.source is None :
                self.run.source = PerformedSource()
            if value!='' :
                self.run.source.performed_by = value
            self.keys_used.append(key)
        elif self.performed_date_key is not None and key==self.performed_date_key :
            if self.run.source is None :
                self.run.source = PerformedSource()
            if value!='' :
                self.run.source.performed_date = value
            self.keys_used.append(key)
        else :
            super().process_other_key(key,value,record)
