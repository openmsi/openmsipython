#imports
from abc import abstractmethod
from gemd.entity.value import DiscreteCategorical, NominalReal
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter
from gemd.entity.object import ProcessSpec,MaterialSpec
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

        If values in the record for any given keys are "''", the Property is not added
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
            if value in ('','N/A') :
                return
            name = key.replace(' ','')
            d = self.property_dict[key]
            val = value
            if 'datatype' in d.keys() :
                val = d['datatype'](val)
            temp = None
            if 'template' in d.keys() :
                temp = d['template']
            if d['valuetype']==DiscreteCategorical :
                self.spec.properties.append(PropertyAndConditions(Property(
                    name=name,
                    value=d['valuetype']({val:1.0}),
                    origin='specified',
                    template=temp)))
            else :
                self.spec.properties.append(PropertyAndConditions(Property(
                    name=name,
                    value=d['valuetype'](val,temp.bounds.default_units),
                    origin='specified',
                    template=temp)))
        #add parameters (if any of them are given) to this MaterialSpec's ProcessSpec
        elif key in self.process_parameter_dict.keys() :
            self.keys_used.append(key)
            if value in ('','N/A') :
                return
            name = key.replace(' ','')
            d = self.process_parameter_dict[key]
            val = value
            if 'datatype' in d.keys() :
                val = d['datatype'](val)
            temp = None
            if 'template' in d.keys() :
                temp = d['template']
            if 'valuetype' not in d.keys() :
                raise ValueError(f'ERROR: no valuetype given for process_parameter_dict entry {key}!')
            elif d['valuetype']==NominalReal :
                if 'template' not in d.keys() :
                    raise ValueError(f'ERROR: no template given for process_parameter_dict entry {key}!')
                value = d['valuetype'](val,temp.bounds.default_units)
            elif d['valuetype']==DiscreteCategorical :
                value = d['valuetype']({val:1.0})
            self.spec.process.parameters.append(Parameter(name=name,
                                                          value=value,
                                                          origin='specified',
                                                          template=temp))
        else :
            super().add_other_key(key,value,record)
