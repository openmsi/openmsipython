#imports
from gemd.entity.util import make_instance
from gemd.entity.source.performed_source import PerformedSource
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
from .templates import MaterialProcessingTemplate, ProcessingGeometryTemplate, ProcessingRouteTemplate

class LaserShockSampleSpec(MaterialSpec) :
    """
    GEMD MaterialSpec for a sample in the Laser Shock Lab
    """

    #a list of the names of elements that can make up the material composition
    ELEMENTS = ['Mg','Al','Zr','Ti','Cu','Ni','Be']

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
        #create the ingredients that went into the process 
        #(adds these ingredients as implicit to the process that produced the material)
        for element in self.ELEMENTS :
            matspec = MaterialSpec(name=element)
            ingspec = IngredientSpec(name=element,material=matspec,process=process)
        #create the actual MaterialSpec
        super().__init__(name=name,process=process,properties=properties)

class LaserShockSample(MaterialRun) :
    """
    A MaterialRun instance of the LaserShockSampleSpec 
    can be instantiated from a filemaker record
    """

    #a list of record keys that will be added just as tags
    TAG_KEYS = ['Sample ID','Supplier Product ID','Date','Performed By','Grant Funding','recordId','modId']
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

    @classmethod
    def from_filemaker_record(cls,record) :
        """
        Use the information in a given FileMaker record to populate and return a LaserShockSample
        """
        #make a placeholder MaterialRun using the make_instance utility
        spec = LaserShockSampleSpec()
        obj = make_instance(spec)
        #loop over the keys and values in the given record and use them to populate the Run
        for key, value in zip(record.keys(),record.values()) :
            #add tags by just appending to the list
            if key in cls.TAG_KEYS :
                obj.tags.append(f'{key.replace(" ","")}::{value.replace(" ","_")}')
            #add measured properties (if any of them are given) by creating MeasurementRuns linked to this MaterialRun
            elif key in cls.MEASURED_PROPERTIES.keys() :
                if value=='' :
                    continue
                name = key.replace(' ','')
                prop_tuple = cls.MEASURED_PROPERTIES[key]
                meas = MeasurementRun(name=name,material=obj)
                meas.spec = MeasurementSpec(name=name)
                meas.properties.append(Property(name=name,
                                                value=prop_tuple[0](prop_tuple[1](value),
                                                                    origin='measured',**prop_tuple[2])))
            #add the category of material it is (a property it's spec'd to have)
            elif key=='Material Processing' :
                for prop in obj.spec.properties :
                    if prop.name=='MaterialProcessing' :
                        prop.property.value=DiscreteCategorical({value:1.0})
                        break
            #add the discrete categorical process parameters
            elif key in cls.DISCRETE_CATEGORICAL_PARS :
                for par in obj.process.parameters :
                    if par.name==key.replace(' ','') :
                        par.value=DiscreteCategorical({value:1.0})
                        break
            #add the other process parameters
            elif key in cls.OTHER_PARS.keys() :
                par_tuple = cls.OTHER_PARS[key]
                for par in obj.process.parameters :
                    if par.name==key.replace(' ','') :
                        par.value = par_tuple[0](prop_tuple[1](value),**prop_tuple[2])
                        break
            #add any recognized constituents by pairing them with their percentages and modifying ingredients
            elif key.startswith('Constituent') :
                if value=='N/A' :
                    continue
                element = value
                percent = int(record[key.replace('Constituent','Percentage')])
                measure = record['Percentage Measure']
                for ing in obj.process.ingredients :
                    if ing.name==element :
                        if measure=='Weight Percent' :
                            ing.mass_fraction = NominalReal(0.01*percent,units='')
                        elif measure=='Atomic Percent' :
                            ing.number_fraction = NominalReal(0.01*percent,units='')
                        else :
                            raise ValueError(f'ERROR: Percentage Measure {measure} not recognized!')
            #add the name of the supplier and purchase/manufacture date as the process source
            elif key=='Supplier Name' :
                date=record['Purchase/Manufacture Date']
                if date=='' :
                    date = None
                obj.process.source = PerformedSource(performed_by=value,performed_date=date)
            #add the sample name
            elif key=='Sample Name' :
                obj.name = value
            #add the general notes
            elif key=='General Notes' :
                obj.notes = value
            #skip keys that are used in processing others
            elif (key.startswith('Percentage')) or (key in ['Purchase/Manufacture Date']) :
                continue
            else :
                errmsg = f'ERROR: unrecognized key for key,value pair ({key},{value}) in FileMaker record '
                errmsg+= f'{record}'
                raise ValueError(errmsg)
        #return the completed object
        return obj
