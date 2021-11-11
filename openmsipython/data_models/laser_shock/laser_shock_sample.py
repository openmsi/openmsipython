#imports
from gemd.entity.value import DiscreteCategorical, NominalReal, NominalComposition
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter, Condition
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .laser_shock_spec_for_run import LaserShockSpecForRun
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockSampleSpec(LaserShockSpecForRun) :
    """
    General constructor for all LaserShockSample Material Specs
    """

    spec_type = MaterialSpec

    def __init__(self,*args,**kwargs) :
        self.mat_type = kwargs.get('mat_type')
        self.pct_meas = kwargs.get('pct_meas')
        self.constituents = kwargs.get('constituents')
        self.preproc = kwargs.get('preproc')
        self.preproc_temp = kwargs.get('preproc_temp')
        self.mat_proc = kwargs.get('mat_proc')
        self.proc_geom = kwargs.get('proc_geom')
        self.proc_route = kwargs.get('proc_route')
        self.proc_temp_1 = kwargs.get('proc_temp_1')
        self.proc_temp_2 = kwargs.get('proc_temp_2')
        self.proc_temp_3 = kwargs.get('proc_temp_3')
        self.proc_temp_4 = kwargs.get('proc_temp_4')
        self.proc_time = kwargs.get('proc_time')
        self.ann_time = kwargs.get('ann_time')
        self.ann_temp = kwargs.get('ann_temp')
        super().__init__(*args,**kwargs)

    def get_spec_kwargs(self) :
        spec_kwargs = {}
        #name
        spec_kwargs['name'] = 'Laser Shock Sample'
        #notes
        spec_kwargs['notes'] = 'One of the possible Specs for producing Samples for the Laser Shock Lab'
        #process
        spec_kwargs['process'] = self.__get_process()
        #the template
        spec_kwargs['template']=OBJ_TEMPL['Sample']
        return spec_kwargs

    def __get_process(self) :
        """
        Returns the spec for the process that created this material
        """
        #begin by defining the raw material
        comp_dict = {}
        for c in self.constituents :
            comp_dict[c[0]]=c[1]
        raw_mat_spec = MaterialSpec(
            name='Raw Material',
            properties=[
                PropertyAndConditions(Property(name='MaterialType',
                                               value=DiscreteCategorical({self.mat_type:1.0}),
                                               template=ATTR_TEMPL['Sample Material Type'],
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
        #some variables to use while dynamically figuring out the process
        proc_to_take_raw_material = None
        input_material_for_next = None
        final_output_proc = None
        #Define sample preprocessing
        if ( (self.preproc is not None and self.preproc!='') or 
             (self.preproc_temp is not None and self.preproc_temp!='') ) :
            preprocessing = ProcessSpec(
                name='Sample Preprocessing',
                conditions=[],
                parameters=[],
                template=OBJ_TEMPL['Sample Preprocessing'],
            )
            if self.preproc is not None and self.preproc!='' :
                preprocessing.conditions.append(
                    Condition(
                        name='Preprocessing',
                        value=DiscreteCategorical({self.preproc:1.0}),
                        template=ATTR_TEMPL['Preprocessing'],
                        origin='specified'
                    )
                )
            if self.preproc_temp is not None and self.preproc_temp!='' :
                temp = ATTR_TEMPL['Preprocessing Temperature']
                preprocessing.parameters.append(
                    Parameter(
                        name='PreprocessingTemperature',
                        value=NominalReal(float(self.preproc_temp),temp.bounds.default_units),
                        template=temp,
                        origin='specified'
                    )
                )
            proc_to_take_raw_material = preprocessing
            input_material_for_next = preprocessing.output_material
            final_output_proc = preprocessing
        #Define sample processing
        sample_processing = ProcessSpec(
            name='Sample Processing',
            conditions=[
                Condition(name='ProcessingGeometry',
                          value=DiscreteCategorical({self.proc_geom:1.0}),
                          template=ATTR_TEMPL['Processing Geometry'],
                          origin='specified'),
                ],
            parameters=[
                        Parameter(name='ProcessingRoute',
                                  value=DiscreteCategorical({self.proc_route:1.0}),
                                  template=ATTR_TEMPL['Processing Route'],
                                  origin='specified'),
                ],
            template=OBJ_TEMPL['Sample Processing']
            )
        #add some optional conditions
        if self.mat_proc is not None and self.mat_proc!='' and len(self.mat_proc.split('\r'))>1 :
            for mp in self.mat_proc.split('\r')[1:] :
                sample_processing.conditions.append(
                    Condition(name='MaterialProcessing',
                          value=DiscreteCategorical({mp:1.0}),
                          template=ATTR_TEMPL['Material Processing'],
                          origin='specified'),
                )
        proc_temps = [self.proc_temp_1,self.proc_temp_2,self.proc_temp_3,self.proc_temp_4]
        for ipt,pt in enumerate(proc_temps,start=1) :
            if pt is not None and pt!='' :
                sample_processing.conditions.append(
                    Condition(name=f'ProcessingTemperature{ipt}',
                              value=NominalReal(float(pt),
                                                ATTR_TEMPL['Processing Temperature'].bounds.default_units),
                              template=ATTR_TEMPL['Processing Temperature'],
                              origin='specified')
                )
        #add some optional parameters
        if self.proc_time!='' :
            sample_processing.parameters.append(Parameter(
                name='ProcessingTime',
                value=NominalReal(float(self.proc_time),ATTR_TEMPL['Processing Time'].bounds.default_units),
                template=ATTR_TEMPL['Processing Time'],
                origin='specified')
            )
        #define the input to processing if preprocessing was performed
        if input_material_for_next is not None :
            IngredientSpec(name='Preprocessed Material',
                           material=input_material_for_next,
                           process=sample_processing,
            )
        input_material_for_next = sample_processing.output_material
        #if preprocessing wasn't performed, set processing to take the raw material
        if proc_to_take_raw_material is None :
            proc_to_take_raw_material = sample_processing
        #reset the output process
        final_output_proc = sample_processing
        #Define the annealing process
        if (self.ann_temp is not None and self.ann_temp!='') and (self.ann_time is not None and self.ann_time!='') :
            annealing = ProcessSpec(
                name='Sample Annealing',
                conditions=[],
                parameters=[],
                template=OBJ_TEMPL['Sample Annealing'],
            )
            #optional conditions
            if self.ann_temp is not None and self.ann_temp!='' :
                annealing.conditions.append(
                    Condition(name='AnnealingTemperature',
                              value=NominalReal(float(self.ann_temp),
                                                ATTR_TEMPL['Annealing Temperature'].bounds.default_units),
                              template=ATTR_TEMPL['Annealing Temperature'],
                              origin='specified')
                    )
            #optional parameters
            if self.ann_time is not None and self.ann_time!='' :
                annealing.parameters.append(
                    Parameter(name='AnnealingTime',
                              value=NominalReal(float(self.ann_time),ATTR_TEMPL['Annealing Time'].bounds.default_units),
                              template=ATTR_TEMPL['Annealing Time'],
                              origin='specified')
                )
            #define the input to annealing
            if input_material_for_next is not None :
                IngredientSpec(name='Processed Material',
                               material=input_material_for_next,
                               process=annealing,
                )
            #reset the output process
            final_output_proc = annealing
        #add the raw material as the ingredient to the process that takes it
        IngredientSpec(name='Raw Material',
                       material=raw_mat_spec,
                       process=proc_to_take_raw_material,
            )
        return final_output_proc


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
        rd = {'Bulk Wave  Speed':{'valuetype':NominalReal,
                                  'datatype':float,
                                  'template':ATTR_TEMPL['Bulk Wave Speed']}}
        for name in ['Density','Bulk Modulus','Average Grain Size','Min Grain Size','Max Grain Size'] :
            rd[name] = {'valuetype':NominalReal,
                        'datatype':float,
                        'template':ATTR_TEMPL[name]}
        return rd

    def get_spec_kwargs(self,record) :
        kwargs = {}
        kwargs['mat_type'] = record.pop('Material Type')
        kwargs['pct_meas'] = record.pop('Percentage Measure')
        constituents = []
        for i in range(1,8) :
            element = record.pop(f'Constituent {i}')
            percentage = record.pop(f'Percentage {i}')
            if element!='N/A' and percentage!=0 :
                constituents.append((element,percentage))
        constituents.sort(key=lambda x:x[0])
        kwargs['constituents'] = constituents
        kwargs['preproc'] = record.pop('Preprocessing')
        kwargs['preproc_temp'] = record.pop('Preprocessing Temperature')
        kwargs['mat_proc'] = record.pop('Material Processing')
        kwargs['proc_geom'] = record.pop('Processing Geometry')
        kwargs['proc_route'] = record.pop('Processing Route')
        kwargs['proc_temp_1'] = record.pop('Processing Temperature 1')
        kwargs['proc_temp_2'] = record.pop('Processing Temperature 2')
        kwargs['proc_temp_3'] = record.pop('Processing Temperature 3')
        kwargs['proc_temp_4'] = record.pop('Processing Temperature 4')
        kwargs['proc_time'] = record.pop('Processing Time')
        kwargs['ann_time'] = record.pop('Annealing Time')
        kwargs['ann_temp'] = record.pop('Annealing Temperature')
        return kwargs
