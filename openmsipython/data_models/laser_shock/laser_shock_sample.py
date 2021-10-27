#imports
from hashlib import sha512
from gemd.entity.value import DiscreteCategorical, NominalReal, NominalComposition
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter, Condition
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .laser_shock_spec import LaserShockSpec
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockSampleSpec(LaserShockSpec) :
    """
    General constructor for all LaserShockSample Material Specs
    """

    spec_type = MaterialSpec

    def __init__(self,*args,**kwargs) :
        self.mat_type = kwargs.get('mat_type')
        self.pct_meas = kwargs.get('pct_meas')
        self.constituents = kwargs.get('constituents')
        self.proc_geom = kwargs.get('proc_geom')
        self.proc_route = kwargs.get('proc_route')
        self.proc_temp = kwargs.get('proc_temp')
        self.proc_time = kwargs.get('proc_time')
        super().__init__(*args,**kwargs)

    def get_arg_hash(self) :
        arg_hash = sha512()
        arg_hash.update(self.mat_type.encode())
        arg_hash.update(self.pct_meas.encode())
        for c in self.constituents :
            arg_hash.update(c[0].encode())
            arg_hash.update(str(c[1]).encode())
        arg_hash.update(self.proc_geom.encode())
        arg_hash.update(self.proc_route.encode())
        arg_hash.update(str(self.proc_temp).encode())
        return arg_hash.hexdigest()

    def get_spec_kwargs(self) :
        spec_kwargs = {}
        #name
        spec_kwargs['name'] = 'Laser Shock Sample'
        #notes
        spec_kwargs['notes'] = 'One of the possible Specs for producing Samples for the Laser Shock Lab'
        #process
        spec_kwargs['process'] = ProcessSpec(
            name='Sample Processing',
            conditions=[Condition(name='ProcessingGeometry',
                                  value=DiscreteCategorical({self.proc_geom:1.0}),
                                  template=ATTR_TEMPL['Processing Geometry'],
                                  origin='specified'),
                        Condition(name='ProcessingTemperature',
                                  value=NominalReal(self.proc_temp,
                                                    ATTR_TEMPL['Processing Temperature'].bounds.default_units),
                                  template=ATTR_TEMPL['Processing Temperature'],
                                  origin='specified')
                ],
            parameters=[
                        Parameter(name='ProcessingRoute',
                                  value=DiscreteCategorical({self.proc_route:1.0}),
                                  template=ATTR_TEMPL['Processing Route'],
                                  origin='specified'),
                        Parameter(name='ProcessingTime',
                                  value=NominalReal(self.proc_time if self.proc_time!='' else -1,
                                                    ATTR_TEMPL['Processing Time'].bounds.default_units),
                                  template=ATTR_TEMPL['Processing Time'],
                                  origin='specified'),
                ],
            template=OBJ_TEMPL['Sample Processing']
            )
        #add the raw material as the ingredient to the process
        comp_dict = {}
        for c in self.constituents :
            comp_dict[c[0]]=c[1]
        raw_mat_spec = MaterialSpec(
            name='Raw Material',
            properties=[
                PropertyAndConditions(Property(name='MaterialProcessing',
                                               value=DiscreteCategorical({self.mat_type:1.0}),
                                               template=ATTR_TEMPL['Sample Material Processing'],
                                               origin='specified')),
                PropertyAndConditions(Property(name='MaterialComposition',
                                               value=NominalComposition(comp_dict),
                                               template=ATTR_TEMPL['Sample Raw Material Composition'],
                                               origin='specified'),
                                      Condition(name='CompositionMeasure',
                                                value=DiscreteCategorical({self.pct_meas:1.0}),
                                                template=ATTR_TEMPL['Composition Measure'],
                                                origin='specified')),
                ],
            template=OBJ_TEMPL['Raw Sample Material'],
            )
        IngredientSpec(name='Raw Material',
                       material=raw_mat_spec,
                       process=spec_kwargs['process'],
            )
        #the template
        spec_kwargs['template']=OBJ_TEMPL['Sample']
        return spec_kwargs

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
                'Bulk Modulus':{'valuetype':NominalReal,
                                'datatype':float,
                                'template':ATTR_TEMPL['Bulk Modulus']},
                'Average Grain Size':{'valuetype':NominalReal,
                                      'datatype':float,
                                      'template':ATTR_TEMPL['Average Grain Size']},
                'Min Grain Size':{'valuetype':NominalReal,
                                  'datatype':float,
                                  'template':ATTR_TEMPL['Min Grain Size']},
                'Max Grain Size':{'valuetype':NominalReal,
                                  'datatype':float,
                                  'template':ATTR_TEMPL['Max Grain Size']},
            }

    def get_spec_kwargs(self,record) :
        kwargs = {}
        kwargs['mat_type'] = record.pop('Material Processing')
        kwargs['pct_meas'] = record.pop('Percentage Measure')
        constituents = []
        for i in range(1,8) :
            element = record.pop(f'Constituent {i}')
            percentage = record.pop(f'Percentage {i}')
            if element!='N/A' and percentage!=0 :
                constituents.append((element,percentage))
        constituents.sort(key=lambda x:x[0])
        kwargs['constituents'] = constituents
        kwargs['proc_geom'] = record.pop('Processing Geometry')
        kwargs['proc_route'] = record.pop('Processing Route')
        kwargs['proc_temp'] = record.pop('Processing Temperature')
        kwargs['proc_time'] = record.pop('Processing Time')
        return kwargs
