#imports
from abc import abstractmethod
from gemd.entity.util import make_instance
from gemd.entity.value import DiscreteCategorical
from gemd.entity.source.performed_source import PerformedSource
from gemd.entity.attribute import Property
from gemd.entity.object import MeasurementSpec, MeasurementRun
from .utilities import name_value_template_from_key_value_dict
from .from_filemaker_record import FromFileMakerRecordBase

class RunFromFileMakerRecord(FromFileMakerRecordBase) :
    """
    An class to provide functionality for using FileMaker records 
    to create and/or link GEMD "Spec" and Run" objects
    """

    def __init__(self,record) :
        """
        Use the information in a given FileMaker record to populate this Run object
        """
        #figure out the Spec for this Run
        spec = self.get_spec(record)
        #create an initial object from the spec
        self.__run = make_instance(spec)
        #set the name of the Run from the Spec if there is no key defining the name
        if self.name_key is None :
            self.__run.name=self.__spec.name
        #call the base class's __init__ with the run as the object to modify
        super().__init__(record,self.__run)

    @property
    @abstractmethod
    def spec_type(self) :
        """
        A property for the type of spec corresponding to this Run object
        (must be a property of child classes)
        """
        pass

    @abstractmethod
    def get_spec_kwargs(self,record) :
        """
        Return the keyword arguments that should be sent to the corresponding spec's 
        constructor method given a FileMaker record
        (must be implemented in child classes)
        """
        pass

    def get_spec(self,record) :
        """
        A function to return the Spec for this Run given a FileMaker record
        """
        kwargs = self.get_spec_kwargs(record)
        new_spec = self.spec_type(**kwargs)
        return new_spec.spec

    @property
    def run(self) :
        return self.__run

class HasSourceFromFileMakerRecord(RunFromFileMakerRecord) :
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

class MaterialRunFromFileMakerRecord(HasSourceFromFileMakerRecord) :
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

        If values in the record for any given keys are "''" or "N/A", the MeasurementRun 
        is not added to the material, but the key is still marked as consumed.

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

    def add_other_key(self,key,value,record) :
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
            name, value, temp = name_value_template_from_key_value_dict(key,value,self.measured_property_dict[key])
            if name is None or value is None :
                return
            meas = MeasurementRun(name=name,material=self.run)
            meas.spec = MeasurementSpec(name=name)
            meas.properties.append(Property(name=name,
                                            value=value,
                                            origin='measured',
                                            template=temp))
        else :
            super().add_other_key(key,value,record)

class MeasurementRunFromFileMakerRecord(HasSourceFromFileMakerRecord) :
    """
    Class to use for creating Measurement(Spec/Run)s based on FileMaker records
    """

    def __init__(self,*args,material=None,**kwargs) :
        """
        material = the MaterialRun whose properties this measurement determined
        """
        super().__init__(*args,**kwargs)
        self.run.material=material

    @property
    def measured_property_dict(self) :
        """
        A dictionary whose keys are FileMaker record keys corresponding to single  
        properties measured during the run. Values for each key are themselves 
        dictionaries specifying details of the properties. 

        If values in the record for any given keys are "''", the Property is not added
        to the MeasurementRun, but the key is still marked as consumed.

        The allowed keys and values for each entry's characteristic dictionary are:
        valuetype:   the BaseValue object type for the Property
        datatype:    datatype to which the value from the FileMaker record should be cast 
                     when added to the Value of the Property
        template:    the AttributeTemplate defining the Property
        """
        return {}

    def add_other_key(self,key,value,record) :
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
        #add measured properties (if any of them are given)
        elif key in self.measured_property_dict.keys() :
            self.keys_used.append(key)
            name, value, temp = name_value_template_from_key_value_dict(key,value,self.measured_property_dict[key])
            if name is None or value is None :
                return
            self.run.properties.append(Property(name=name,
                                                value=value,
                                                origin='measured',
                                                template=temp))
        else :
            super().add_other_key(key,value,record)
