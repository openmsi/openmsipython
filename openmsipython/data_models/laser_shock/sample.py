#imports
from typing import final
from gemd.entity.value import NominalCategorical, NominalReal, NominalComposition
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter, Condition
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec
from ..spec_for_run import SpecForRun
from ..run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockSampleSpec(SpecForRun) :
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
        spec_kwargs['template']=self.templates.obj('Sample')
        return spec_kwargs

    def __get_process(self) :
        """
        Returns the spec for the process that created this material
        """
        #begin by defining the raw material
        comp_dict = {}
        for c in self.constituents :
            comp_dict[c[0]]=c[1]
        raw_mat_properties = []
        if comp_dict!={} :
            condition = None
            if self.pct_meas not in ('','N/A') :
                condition = Condition(name='CompositionMeasure',
                                      value=NominalCategorical(str(self.pct_meas)),
                                      template=self.templates.attr('Composition Measure'),
                                      origin='specified')
            raw_mat_properties.append(
                PropertyAndConditions(Property(name='MaterialComposition',
                                               value=NominalComposition(comp_dict),
                                               template=self.templates.attr('Sample Raw Material Composition'),
                                               origin='specified'),condition)
                )
        raw_mat_spec = MaterialSpec(
            name='Raw Material',
            properties=raw_mat_properties,
            template=self.templates.obj('Raw Sample Material'),
            )
        if self.mat_type!='' :
            raw_mat_spec.properties.append(
                PropertyAndConditions(Property(name='MaterialType',
                                               value=NominalCategorical(str(self.mat_type)),
                                               template=self.templates.attr('Sample Material Type'),
                                               origin='specified')),
            )
        #some variables to use while dynamically figuring out the process
        all_procs = []
        proc_to_take_raw_material = None
        preprocessed=False
        final_output_proc = None
        #Define sample preprocessing
        if ( (self.preproc is not None and self.preproc!='') or 
             (self.preproc_temp is not None and self.preproc_temp!='') ) :
            preprocessed = True
            preprocessing = ProcessSpec(
                name='Sample Preprocessing',
                conditions=[],
                parameters=[],
                template=self.templates.obj('Sample Preprocessing'),
            )
            if self.preproc is not None and self.preproc!='' :
                preprocessing.conditions.append(
                    Condition(
                        name='Preprocessing',
                        value=NominalCategorical(str(self.preproc)),
                        template=self.templates.attr('Preprocessing'),
                        origin='specified'
                    )
                )
            if self.preproc_temp is not None and self.preproc_temp!='' :
                temp = self.templates.attr('Preprocessing Temperature')
                preprocessing.parameters.append(
                    Parameter(
                        name='PreprocessingTemperature',
                        value=NominalReal(float(self.preproc_temp),temp.bounds.default_units),
                        template=temp,
                        origin='specified'
                    )
                )
            #create a preprocessed sample
            MaterialSpec(name='Preprocessed Material',process=preprocessing)
            all_procs.append(preprocessing)
            proc_to_take_raw_material = preprocessing
            final_output_proc = preprocessing
        #Define sample processing
        sample_processing_conditions = []
        sample_processing_parameters = []
        if self.proc_geom!='' :
            sample_processing_conditions.append(
                Condition(name='ProcessingGeometry',
                          value=NominalCategorical(str(self.proc_geom)),
                          template=self.templates.attr('Processing Geometry'),
                          origin='specified')
            )
        if self.proc_route!='' :
            sample_processing_parameters.append(
                Parameter(name='ProcessingRoute',
                                  value=NominalCategorical(str(self.proc_route)),
                                  template=self.templates.attr('Processing Route'),
                                  origin='specified'),
            )
        sample_processing = ProcessSpec(
            name='Sample Processing',
            conditions=sample_processing_conditions,
            parameters=sample_processing_parameters,
            template=self.templates.obj('Sample Processing')
            )
        #add some optional conditions
        if self.mat_proc is not None and self.mat_proc!='' and len(self.mat_proc.split('\r'))>1 :
            for mp in self.mat_proc.split('\r')[1:] :
                sample_processing.conditions.append(
                    Condition(name='MaterialProcessing',
                          value=NominalCategorical(str(mp)),
                          template=self.templates.attr('Material Processing'),
                          origin='specified'),
                )
        proc_temps = [self.proc_temp_1,self.proc_temp_2,self.proc_temp_3,self.proc_temp_4]
        for ipt,pt in enumerate(proc_temps,start=1) :
            if pt is not None and pt!='' :
                sample_processing.conditions.append(
                    Condition(name=f'ProcessingTemperature{ipt}',
                              value=NominalReal(float(pt),
                                                self.templates.attr('Processing Temperature').bounds.default_units),
                              template=self.templates.attr('Processing Temperature'),
                              origin='specified')
                )
        #add some optional parameters
        if self.proc_time!='' :
            sample_processing.parameters.append(Parameter(
                name='ProcessingTime',
                value=NominalReal(float(self.proc_time),self.templates.attr('Processing Time').bounds.default_units),
                template=self.templates.attr('Processing Time'),
                origin='specified')
            )
        #define the input to processing
        if preprocessed :
            IngredientSpec(name='Preprocessed Material',
                           material=preprocessing.output_material,
                           process=sample_processing,
            )
        else :
            proc_to_take_raw_material = sample_processing
        #add processing to the list of processes
        all_procs.append(sample_processing)
        #reset the output process
        final_output_proc = sample_processing
        #Define the annealing process
        if (self.ann_temp is not None and self.ann_temp!='') and (self.ann_time is not None and self.ann_time!='') :
            annealing = ProcessSpec(
                name='Sample Annealing',
                conditions=[],
                parameters=[],
                template=self.templates.obj('Sample Annealing'),
            )
            #optional conditions
            if self.ann_temp is not None and self.ann_temp!='' :
                annealing.conditions.append(
                    Condition(name='AnnealingTemperature',
                              value=NominalReal(float(self.ann_temp),
                                                self.templates.attr('Annealing Temperature').bounds.default_units),
                              template=self.templates.attr('Annealing Temperature'),
                              origin='specified')
                    )
            #optional parameters
            if self.ann_time is not None and self.ann_time!='' :
                annealing.parameters.append(
                    Parameter(name='AnnealingTime',
                              value=NominalReal(float(self.ann_time),
                                                self.templates.attr('Annealing Time').bounds.default_units),
                              template=self.templates.attr('Annealing Time'),
                              origin='specified')
                )
            #define the input to annealing
            MaterialSpec(name='Processed Material',process=sample_processing)
            IngredientSpec(name='Processed Material',
                            material=sample_processing.output_material,
                            process=annealing,
            )
            #reset the output process
            all_procs.append(annealing)
            final_output_proc = annealing
        #add the raw material as the ingredient to the process that takes it
        IngredientSpec(name='Raw Material',
                    material=raw_mat_spec,
                    process=proc_to_take_raw_material,
            )
        for proc in all_procs :
            if proc!=final_output_proc :
                _ = self.specs.unique_version_of(proc)
        return self.specs.unique_version_of(final_output_proc)

class LaserShockSample(MaterialRunFromFileMakerRecord) :
    """
    A MaterialSpec/MaterialRun pair representing a Sample in the Laser Shock Lab 
    created from a record in the "Sample" layout of the FileMaker database
    """

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
                                  'template':self.templates.attr('Bulk Wave Speed')}}
        for name in ['Density','Bulk Modulus','Average Grain Size','Min Grain Size','Max Grain Size'] :
            rd[name] = {'valuetype':NominalReal,
                        'datatype':float,
                        'template':self.templates.attr(name)}
        return rd

    @property
    def unique_values(self):
        return {**super().unique_values,self.name_key:self.run.name}

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
