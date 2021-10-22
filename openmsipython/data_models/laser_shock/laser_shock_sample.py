#imports
from hashlib import sha512
from gemd.entity.value import DiscreteCategorical, NominalReal, NominalComposition
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter, Condition
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockSampleSpec :
    """
    General constructor for all LaserShockSample Material Specs
    """

    def __init__(self,mat_type,pct_meas,constituents,proc_geom,proc_route,proc_temp) :
        #keep the arguments around for quick comparison with other potential specs
        self.args = [mat_type,pct_meas,constituents,proc_geom,proc_route,proc_temp]
        #create the unique name for the spec
        name_hash = sha512()
        name_hash.update('Laser Shock Sample'.encode())
        name_hash.update(mat_type.encode())
        name_hash.update(pct_meas.encode())
        for c in constituents :
            name_hash.update(c[0].encode())
            name_hash.update(str(c[1]).encode())
        name_hash.update(proc_geom.encode())
        name_hash.update(proc_route.encode())
        name_hash.update(str(proc_temp).encode())
        name = name_hash.hexdigest()
        #notes
        notes = 'One of the possible Specs for producing Samples for the Laser Shock Lab'
        #process
        process = ProcessSpec(
            name=name,
            conditions=[Condition(name='ProcessingGeometry',
                                  value=DiscreteCategorical({proc_geom:1.0}),
                                  template=ATTR_TEMPL['Processing Geometry'],
                                  origin='specified'),
                        Condition(name='ProcessingTemperature',
                                  value=NominalReal(proc_temp,
                                                    ATTR_TEMPL['Processing Temperature'].bounds.default_units),
                                  template=ATTR_TEMPL['Processing Temperature'],
                                  origin='specified')
                ],
            parameters=[
                        Parameter(name='ProcessingRoute',
                                  value=DiscreteCategorical({proc_route:1.0}),
                                  template=ATTR_TEMPL['Processing Route'],
                                  origin='specified'),
                ],
            )
        #add the raw material as the ingredient to the process
        comp_dict = {}
        for c in constituents :
            comp_dict[c[0]]=c[1]
        raw_mat_spec = MaterialSpec(
            name='Raw Material',
            properties=[
                PropertyAndConditions(Property(name='MaterialProcessing',
                                               value=DiscreteCategorical({mat_type:1.0}),
                                               template=ATTR_TEMPL['Sample Material Processing'],
                                               origin='specified')),
                PropertyAndConditions(Property(name='MaterialComposition',
                                               value=NominalComposition(comp_dict),
                                               template=ATTR_TEMPL['Sample Raw Material Composition'],
                                               origin='specified'),
                                      Condition(name='CompositionMeasure',
                                                value=DiscreteCategorical({pct_meas:1.0}),
                                                template=ATTR_TEMPL['Composition Measure'],
                                                origin='specified')),
                ],
            template=OBJ_TEMPL['Raw Sample Material'],
            )
        IngredientSpec(name='Raw Material',
                       material=raw_mat_spec,
                       process=process,
            )
        #create the actual MaterialSpec
        self.spec = MaterialSpec(name=name,notes=notes,process=process,template=OBJ_TEMPL['Sample'])

class LaserShockSample(MaterialRunFromFileMakerRecord) :
    """
    A MaterialSpec/MaterialRun pair representing a Sample in the Laser Shock Lab 
    created from a record in the "Sample" layout of the FileMaker database
    """

    #Some constants for MaterialRunFromFileMakerRecord
    spec_type = LaserShockSampleSpec
    name_key = 'Sample Name'
    notes_key = 'General Notes'
    performed_by_key = 'Supplier Name'
    performed_date_key = 'Purchase/Manufacture Date'

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Sample ID','Supplier Product ID','Date','Performed By','Grant Funding']

    @property
    def measured_property_dict(self) :
        return {'Density':{'valuetype':NominalReal,
                           'datatype':float,
                           'template':ATTR_TEMPL['Density']},
                'Bulk Wave  Speed':{'valuetype':NominalReal,
                                    'datatype':float,
                                    'template':ATTR_TEMPL['Bulk Wave Speed']},
                'Average Grain Size':{'valuetype':NominalReal,
                                      'datatype':float,
                                      'template':ATTR_TEMPL['Average Grain Size']},
            }

    def get_spec_args(self,record) :
        #get everything that defines the specs
        mat_type = record.pop('Material Processing')
        pct_meas = record.pop('Percentage Measure')
        constituents = []
        for i in range(1,8) :
            element = record.pop(f'Constituent {i}')
            percentage = record.pop(f'Percentage {i}')
            if element!='N/A' and percentage!=0 :
                constituents.append((element,percentage))
        constituents.sort(key=lambda x:x[0])
        proc_geom = record.pop('Processing Geometry')
        proc_route = record.pop('Processing Route')
        proc_temp = record.pop('Processing Temperature')
        args = [mat_type,pct_meas,constituents,proc_geom,proc_route,proc_temp]
        return args
