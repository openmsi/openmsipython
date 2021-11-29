#imports
from abc import abstractmethod
from gemd.entity.value import DiscreteCategorical, NominalReal
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter, Condition
from gemd.entity.object import ProcessSpec, MaterialSpec
from .utilities import name_value_template_origin_from_key_value_dict
from .from_filemaker_record import FromFileMakerRecordBase

class SpecFromFileMakerRecord(FromFileMakerRecordBase) :
    """
    Base class for Spec objects created from FileMaker records
    """

    def __init__(self,record) :
        """
        Create the Spec using the given FileMaker record
        """
        #create a placeholder Spec
        self.__spec = self.spec_type(**self.init_spec_kwargs)
        #call the base class's __init__ with the Spec as the object to modify
        super().__init__(record,self.__spec)

    @property
    def spec(self) :
        return self.__spec

    @property
    def init_spec_kwargs(self) :
        """
        keyword arguments that should be used to define the initial spec
        """
        return {'name':'placeholder'}

    @property
    @abstractmethod
    def name_key(self) :
        """
        Overrides the same property for the base class; specs created from records MUST have this defined
        """
        pass

    @property
    @abstractmethod
    def spec_type(self) :
        """
        A property defining the type of GEMD Spec that this LaserShockSpec creates
        """
        pass

class HasTemplateFromFileMakerRecord(SpecFromFileMakerRecord) :

    @property
    def template(self) :
        """
        A template object defining this Spec
        """
        return None

    @property
    def init_spec_kwargs(self) :
        rd = super().init_spec_kwargs
        if self.template is not None :
            rd['name']=self.template.name
            rd['template']=self.template
        return rd

class MaterialSpecFromFileMakerRecord(HasTemplateFromFileMakerRecord) :

    spec_type = MaterialSpec

    @property
    def process_template(self) :
        """
        property giving the Template used to define the Process that created this Material
        """
        return None

    @property
    def property_dict(self) :
        """
        A dictionary whose keys are FileMaker record keys corresponding to single  
        properties of the material spec. Values for each key are themselves dictionaries, 
        used to add Properties to the Spec. 

        If values in the record for any given keys are "''" or "N/A", the Property is not added
        to the spec, but the key is still marked as consumed.

        The allowed keys and values for each entry's characteristic dictionary are:
        valuetype:   the BaseValue object type for the Property
        datatype:    datatype to which the value from the FileMaker record should be cast 
                     when added to the Value of the Property
        template:    the AttributeTemplate defining the Property
        """
        return {}

    @property
    def process_parameter_dict(self) :
        """
        A dictionary in the same format as "property_dict" above, except entries represent 
        Parameters of the ProcessSpec used to create this MaterialSpec
        """
        return {}

    @property
    def init_spec_kwargs(self) :
        rd = super().init_spec_kwargs
        if self.process_template is not None :
            rd['process'] = ProcessSpec(name=self.process_template.name,template=self.process_template)
        return rd

    @property
    def other_keys(self) :
        return [*super().other_keys,
                *self.property_dict.keys(),
                *self.process_parameter_dict.keys()
               ]

    def add_other_key(self,key,value,record) :
        #add properties (if any of them are given) to this MaterialSpec
        if key in self.property_dict.keys() :
            self.keys_used.append(key)
            name, value, temp, origin = name_value_template_origin_from_key_value_dict(key,value,
                                                                                       self.property_dict[key])
            if name is None or value is None :
                return
            self.spec.properties.append(PropertyAndConditions(
                Property(name=name,
                         value=value,
                         origin=origin if origin is not None else 'specified',
                         template=temp)
                ))
        #add parameters (if any of them are given) to this MaterialSpec's ProcessSpec
        elif key in self.process_parameter_dict.keys() :
            self.keys_used.append(key)
            name, value, temp, origin = name_value_template_origin_from_key_value_dict(key,value,
                                                                                       self.process_parameter_dict[key])
            if name is None or value is None :
                return
            self.spec.process.parameters.append(Parameter(name=name,
                                                          value=value,
                                                          origin=origin if origin is not None else 'specified',
                                                          template=temp))
        else :
            super().add_other_key(key,value,record)

class ProcessSpecFromFileMakerRecord(HasTemplateFromFileMakerRecord) :

    spec_type = ProcessSpec

    @property
    def condition_dict(self) :
        """
        A dictionary whose keys are FileMaker record keys corresponding to single  
        conditions for the process spec. Values for each key are themselves dictionaries, 
        used to add Conditions to the Spec. 

        If values in the record for any given keys are "''" or "N/A", the Property is not added
        to the spec, but the key is still marked as consumed.

        The allowed keys and values for each entry's characteristic dictionary are:
        valuetype:   the BaseValue object type for the Condition
        datatype:    datatype to which the value from the FileMaker record should be cast 
                     when added to the Value of the Condition
        template:    the AttributeTemplate defining the Condition
        """
        return {}

    @property
    def parameter_dict(self) :
        """
        A dictionary in the same format as "condition_dict" above, except entries represent 
        Parameters of the ProcessSpec instead of Conditions
        """
        return {}

    @property
    def other_keys(self) :
        return [*super().other_keys,
                *self.condition_dict.keys(),
                *self.parameter_dict.keys()
               ]

    def add_other_key(self,key,value,record) :
        #add conditions (if any of them are given) to this ProcessSpec
        if key in self.condition_dict.keys() :
            self.keys_used.append(key)
            name, value, temp, origin = name_value_template_origin_from_key_value_dict(key,value,
                                                                                       self.condition_dict[key])
            if name is None or value is None :
                return
            self.spec.conditions.append(Condition(name=name,
                                                  value=value,
                                                  origin=origin if origin is not None else 'specified',
                                                  template=temp))
        #add parameters (if any of them are given) to this ProcessSpec
        elif key in self.parameter_dict.keys() :
            self.keys_used.append(key)
            name, value, temp, origin = name_value_template_origin_from_key_value_dict(key,value,
                                                                                       self.parameter_dict[key])
            if name is None or value is None :
                return
            self.spec.parameters.append(Parameter(name=name,
                                                  value=value,
                                                  origin=origin if origin is not None else 'specified',
                                                  template=temp))
        else :
            super().add_other_key(key,value,record)