#imports
from gemd.entity.value.nominal_real import NominalReal
from gemd.entity.value.discrete_categorical import DiscreteCategorical
from gemd.entity.attribute.parameter import Parameter
from gemd.entity.attribute.property import Property
from gemd.entity.attribute.property_and_conditions import PropertyAndConditions
from gemd.entity.object.ingredient_spec import IngredientSpec
from gemd.entity.object.process_spec import ProcessSpec
from gemd.entity.object.measurement_spec import MeasurementSpec
from gemd.entity.object.measurement_run import MeasurementRun
from gemd.entity.object.material_spec import MaterialSpec
from gemd.entity.object.material_run import MaterialRun
from .attribute_templates import MaterialProcessingTemplate, ProcessingGeometryTemplate, ProcessingRouteTemplate
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockSampleSpec(MaterialSpec) :
    """
    GEMD MaterialSpec for a sample in the Laser Shock Lab
    """

    def __init__(self) :
        #define the arguments to the MaterialSpec
        name = 'Laser Shock Sample'
        process = ProcessSpec(
            name='Laser Shock Sample Processing',
            parameters=[Parameter(name='ProcessingGeometry',
                                  template=ProcessingGeometryTemplate(),
                                  origin='specified'),
                        Parameter(name='ProcessingRoute',
                                  template=ProcessingRouteTemplate(),
                                  origin='specified'),
                        Parameter(name='ProcessingTemperature',
                                  origin='specified')
                ]
            )
        properties = [
            PropertyAndConditions(Property(name='MaterialProcessing',
                                           template=MaterialProcessingTemplate(),
                                           origin='specified')),
        ]
        #create the actual MaterialSpec
        super().__init__(name=name,process=process,properties=properties)

class LaserShockSample(MaterialRun,MaterialRunFromFileMakerRecord) :
    """
    A MaterialRun instance of the LaserShockSampleSpec 
    can be instantiated from a filemaker record
    """

    #Some constants for MaterialRunFromFileMakerRecord
    spec_type = LaserShockSampleSpec
    name_key = 'Sample Name'
    notes_key = 'General Notes'
    tag_keys = ['Sample ID','Supplier Product ID','Date','Performed By','Grant Funding','recordId','modId']
    performed_by_key = 'Supplier Name'
    performed_date_key = 'Purchase/Manufacture Date'

    #Some more internal constants
    #a dictionary keyed by names of possible measured properties whose values are tuples of (ValueType,datatype,kwargs)
    MEASURED_PROPERTIES = {'Density':(NominalReal,float,{'units':'kg/m^3'}),
                           'Bulk Wave  Speed':(NominalReal,float,{'units':'m/s'}),
                           'Average Grain Size':(NominalReal,float,{'units':'um'}),
                           }
    #a list of record keys corresponding to DiscreteCategorical parameters of the process used
    DISCRETE_CATEGORICAL_PARS = ['Processing Geometry','Processing Route']
    #a dictionary keyed by names of non-categorical process parameters 
    #whose values are tuples of (ValueType,datatype,kwargs)
    OTHER_PARS = {'Processing Temperature':(NominalReal,float,{'units':'C'})}

    @property
    @classmethod
    def other_keys(cls) :
        return [*(super(LaserShockSample,cls).other_keys),
                *(cls.MEASURED_PROPERTIES.keys()),
                *(cls.DISCRETE_CATEGORICAL_PARS),
                *(cls.OTHER_PARS.keys()),
                'Material Processing',
                *[f'Constituent {i}' for i in range(1,8)],
                ]

    @classmethod
    def ignore_key(cls,key) :
        if key.startswith('Percentage') :
            return True
        return super(LaserShockSample,cls).ignore_key(key)
    
    @classmethod
    def process_other_key(cls,key,value,record,run_obj) :
        #add measured properties (if any of them are given) by creating MeasurementRuns linked to this MaterialRun
        if key in cls.MEASURED_PROPERTIES.keys() :
            if value=='' :
                return
            name = key.replace(' ','')
            prop_tuple = cls.MEASURED_PROPERTIES[key]
            meas = MeasurementRun(name=name,material=run_obj)
            meas.spec = MeasurementSpec(name=name)
            meas.properties.append(Property(name=name,
                                            value=prop_tuple[0](prop_tuple[1](value),
                                                                origin='measured',**prop_tuple[2])))
        #add the category of material it is (a property it's spec'd to have)
        elif key=='Material Processing' :
            for prop in run_obj.spec.properties :
                if prop.name=='MaterialProcessing' :
                    prop.property.value=DiscreteCategorical({value:1.0})
                    break
        #add the discrete categorical process parameters
        elif key in cls.DISCRETE_CATEGORICAL_PARS :
            for par in run_obj.process.parameters :
                if par.name==key.replace(' ','') :
                    par.value=DiscreteCategorical({value:1.0})
                    break
        #add the other process parameters
        elif key in cls.OTHER_PARS.keys() :
            par_tuple = cls.OTHER_PARS[key]
            for par in run_obj.process.parameters :
                if par.name==key.replace(' ','') :
                    par.value = par_tuple[0](prop_tuple[1](value),**prop_tuple[2])
                    break
        #add any recognized constituents by pairing them with their percentages and adding ingredient specs
        elif key.startswith('Constituent') :
            if value=='N/A' :
                return
            element = value
            percent = int(record[key.replace('Constituent','Percentage')])
            measure = record['Percentage Measure']
            matspec = MaterialSpec(name=element)
            if measure=='Weight Percent' :
                IngredientSpec(name=element,
                               material=matspec,
                               process=run_obj.process.spec,
                               mass_fraction=NominalReal(0.01*percent,units=''))
            elif measure=='Atomic Percent' :
                IngredientSpec(name=element,
                               material=matspec,
                               process=run_obj.process.spec,
                               number_fraction=NominalReal(0.01*percent,units=''))
            else :
                raise ValueError(f'ERROR: Percentage Measure {measure} not recognized!')
        else :
            super(LaserShockSample,cls).process_other_key(key,value,record,run_obj)
