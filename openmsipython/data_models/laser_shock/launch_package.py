#imports 
import copy
from gemd.util.impl import recursive_foreach
from gemd.entity.util import make_instance
from gemd.entity.source.performed_source import PerformedSource
from gemd.entity.value import NominalCategorical, NominalInteger, NominalReal
from gemd.entity.attribute import Property, Parameter, Condition
from gemd.entity.object import ProcessSpec, MaterialSpec, MeasurementRun, IngredientSpec
from ..utilities import search_for_single_name, search_for_single_tag
from ..cached_isinstance_functions import isinstance_ingredient_run
from ..spec_for_run import SpecForRun
from ..run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockLaunchPackageSpec(SpecForRun) :
    """
    Dynamically-created spec for a Launch Package
    """

    spec_type = MaterialSpec

    def __init__(self,*args,**kwargs) :
        self.flyerspec = kwargs.get('flyerspec')
        self.spacerID = kwargs.get('spacerID')
        self.spacercuttingname = kwargs.get('spacercuttingname')
        self.spacercutting = kwargs.get('spacercutting')
        self.spacercuttingenergy = kwargs.get('spacercuttingenergy')
        self.spacercuttingnpasses_1 = kwargs.get('spacercuttingnpasses_1')
        self.spacercuttingnpasses_2 = kwargs.get('spacercuttingnpasses_2')
        self.spacercuttingnpasses_3 = kwargs.get('spacercuttingnpasses_3')
        self.impactsamplespec = kwargs.get('impactsamplespec')
        self.flyerrow = kwargs.get('flyerrow')
        self.flyercol = kwargs.get('flyercol')
        self.use_spacer = kwargs.get('use_spacer')
        self.spacer_attachment = kwargs.get('spacer_attachment')
        self.spacer_adhesive = kwargs.get('spacer_adhesive')
        self.use_sample = kwargs.get('use_sample')
        self.samp_attachments_adhesives = kwargs.get('samp_attachments_adhesives')
        self.samp_orientation = kwargs.get('samp_orientation')
        super().__init__(*args,**kwargs)

    def get_spec_kwargs(self) :
        spec_kwargs = {}
        #name
        spec_kwargs['name'] = 'Launch Package'
        #notes
        spec_kwargs['notes'] = 'A spec for creating a launch package'
        #process
        spec_kwargs['process'] = self.__get_process()
        #the template
        spec_kwargs['template'] = self.templates.obj(spec_kwargs['name'])
        return spec_kwargs

    def __get_process(self) :
        """
        Helper function to return the process spec for this Launch Package spec
        """
        # Choose Flyer from Flyer Stack
        choosing_flyer_params = []
        if self.flyerrow!='' :
            choosing_flyer_params.append(
                Parameter(name='Flyer Row',
                          value=NominalInteger(int(self.flyerrow)),
                          template=self.templates.attr('Flyer Row'),
                          origin='specified')
            )
        if self.flyercol!='' :
            choosing_flyer_params.append(
                Parameter(name='Flyer Column',
                          value=NominalInteger(int(self.flyercol)),
                          template=self.templates.attr('Flyer Column'),
                          origin='specified')
            )
        choosing_flyer = ProcessSpec(
            name='Choosing Flyer',
            parameters=choosing_flyer_params,
            template=self.templates.obj('Choosing Flyer'),
            )
        IngredientSpec(name='Flyer Stack',
                       material=self.flyerspec if self.flyerspec is not None else None,
                       process=choosing_flyer)
        # Create Spacer from Spacer ID and Spacer Cutting Program
        if not self.use_spacer :
            return self.specs.unique_version_of(choosing_flyer)
        else :
            MaterialSpec(name='Chosen Flyer',process=choosing_flyer)
            choosing_flyer = self.specs.unique_version_of(choosing_flyer)
        if self.spacercutting is not None :
            cutting_spacer = copy.deepcopy(self.spacercutting)
            if self.specs.encoder.scope in cutting_spacer.uids.keys() :
                _ = cutting_spacer.uids.pop(self.specs.encoder.scope)
        else :
            cutting_spacer = ProcessSpec(
                name=self.spacercuttingname if self.spacercuttingname!='' else 'Unknown Spacer Cutting',
                template=self.templates.obj('Cutting Spacer')
                )
        if self.spacercuttingenergy!='' :
            temp = self.templates.attr('Laser Cutting Energy')
            laser_cutting_energy_par = None
            for p in cutting_spacer.parameters :
                if p.name=='LaserCuttingEnergy' :
                    laser_cutting_energy_par = p
                    break
            if laser_cutting_energy_par is not None :
                new_value=NominalReal(float(self.spacercuttingenergy),temp.bounds.default_units)
                p.value=new_value
            else :
                cutting_spacer.parameters.append(
                    Parameter(
                        name='LaserCuttingEnergy',
                        value=NominalReal(float(self.spacercuttingenergy),temp.bounds.default_units),
                        template=temp,
                        origin='specified',
                        )
                )
        n_passes_values = [self.spacercuttingnpasses_1,self.spacercuttingnpasses_2,self.spacercuttingnpasses_3]
        for ival,val in enumerate(n_passes_values,start=1) :
            if val!='' :
                n_passes_par = None
                for p in cutting_spacer.parameters :
                    if p.name==f'NumberofPasses{ival}' :
                        n_passes_par = p
                        break
                if n_passes_par is not None :
                    new_value=NominalInteger(int(val))
                    p.value=new_value
                else :
                    cutting_spacer.parameters.append(
                        Parameter(
                            name=f'NumberofPasses{ival}',
                            value=NominalInteger(int(val)),
                            template=self.templates.attr('Number of Passes'),
                            origin='specified',
                            )
                    )
        IngredientSpec(name='Spacer Material',
                       material=self.spacerID if self.spacerID is not None else None,
                       process=cutting_spacer)
        MaterialSpec(name='Cut Spacer',process=cutting_spacer)
        cutting_spacer = self.specs.unique_version_of(cutting_spacer)
        if cutting_spacer!=self.spacercutting and 'ObjectType::LaserShockSpacerCuttingProgram' in cutting_spacer.tags :
            cutting_spacer.tags.remove('ObjectType::LaserShockSpacerCuttingProgram')
        # Attach Spacer to Flyer
        attaching_spacer = ProcessSpec(
            name='Attaching Spacer',
            conditions=[
                Condition(name='Spacer Attachment Method',
                          value=NominalCategorical(str(self.spacer_attachment)),
                          template=self.templates.attr('Spacer Attachment Method'),
                          origin='specified'),
                ],
            parameters=[
                Parameter(name='Spacer Adhesive',
                          value=NominalCategorical(str(self.spacer_adhesive)),
                          template=self.templates.attr('Spacer Adhesive'),
                          origin='specified'),
                ],
            template=self.templates.obj('Attaching Spacer')
            )
        IngredientSpec(name='Chosen Flyer',material=choosing_flyer.output_material,process=attaching_spacer)
        IngredientSpec(name='Cut Spacer',material=cutting_spacer.output_material,process=attaching_spacer)
        # Attach Impact Sample to Flyer and Spacer stack
        if not self.use_sample :
            return self.specs.unique_version_of(attaching_spacer)
        else :
            MaterialSpec(name='Flyer and Spacer',process=attaching_spacer)
            attaching_spacer = self.specs.unique_version_of(attaching_spacer)
        params = []
        if self.samp_orientation!='' :
            params.append(
                Parameter(name='Sample Orientation',
                          value=NominalCategorical(str(self.samp_orientation)),
                          template=self.templates.attr('Sample Orientation'),
                          origin='specified',
                    )
            )
        attaching_sample = ProcessSpec(
            name='Attaching Sample',
            parameters=params,
            template=self.templates.obj('Attaching Sample')
            )
        for ai,a in enumerate(self.samp_attachments_adhesives) :
            if ai==0 :
                attaching_sample.conditions.append(
                    Condition(name='Sample Attachment Method',
                              value=NominalCategorical(str(a)),
                              template=self.templates.attr('Sample Attachment Method'),
                              origin='specified')
                    )
            else :
                attaching_sample.parameters.append(
                    Parameter(name='Sample Attachment Adhesive',
                              value=NominalCategorical(str(a)),
                              template=self.templates.attr('Sample Attachment Adhesive'),
                              origin='specified')
                    )
        IngredientSpec(name='Flyer and Spacer',material=attaching_spacer.output_material,process=attaching_sample)
        IngredientSpec(name='Impact Sample',
                       material=self.impactsamplespec if self.impactsamplespec is not None else None,
                       process=attaching_sample)
        attaching_sample = self.specs.unique_version_of(attaching_sample)
        return attaching_sample

class LaserShockLaunchPackage(MaterialRunFromFileMakerRecord) :
    """
    A representation of a Launch Package in the Laser Shock Lab, created using a FileMaker record
    """

    spec_type = LaserShockLaunchPackageSpec

    name_key = 'Launch ID'
    performed_by_key = 'Performed By'
    performed_date_key = 'Date'

    #################### PROPERTIES ####################

    @property
    def tags_keys(self):
        return [*super().tags_keys,'Secondary Sample ID']
    
    @property
    def other_keys(self) :
        return [*super().other_keys,
                'Spacer Inner Diameter','Spacer Outer Diameter',
                'Sample Diameter','Sample Thickness',
            ]

    @property
    def unique_values(self):
        return {**super().unique_values,self.name_key:self.run.name}

    #################### PUBLIC FUNCTIONS ####################
    
    def __init__(self,record,flyer_stacks,spacer_IDs,spacer_cutting_programs,samples,**kwargs) :
        # find the flyer stack, spacer ID, spacer cutting program, and sample that were used
        self.flyerstack = search_for_single_tag([fs for fs in flyer_stacks],'FlyerID',
                                                record.pop('Flyer ID').replace(' ','_'))
        self.spacerID = search_for_single_name([sid for sid in spacer_IDs],
                                               record.pop('Spacer Type'),logger=kwargs.get('logger'))
        self.spacercuttingname = record.pop('Spacer Cutting Program')
        self.spacercutting = search_for_single_name([scp for scp in spacer_cutting_programs],
                                                    self.spacercuttingname,logger=kwargs.get('logger'))
        self.sample = search_for_single_name([s for s in samples],
                                             record.pop('Sample Name'),logger=kwargs.get('logger'))
        # create Runs from Specs that were found
        self.spacer = make_instance(self.spacerID) if self.spacerID is not None else None
        # create the Impact Sample that was cut from the original sample
        self.impactsample = self.__get_impact_sample(record,kwargs.get('templates'),kwargs.get('specs'))
        # create the rest of the Run
        super().__init__(record,**kwargs)
        # link some objects back into the created Run
        recursive_foreach(self.run.process.ingredients,self.__make_replacements,apply_first=True)

    def add_other_key(self,key,value,record) :
        # Measured properties of spacer
        if key in ['Spacer Inner Diameter','Spacer Outer Diameter'] :
            self.keys_used.append(key)
            if value=='' :
                return
            if self.spacer is None :
                errmsg = f'ERROR: {key} measurement ({value}) found for a Launch Package with no spacer!'
                self.logger.error(errmsg,ValueError)
            name=key.replace(' ','')
            meas = MeasurementRun(name=name,material=self.spacer)
            temp = self.templates.attr('Spacer Diameter')
            meas.properties.append(Property(name=name,
                                            value=NominalReal(float(value),temp.bounds.default_units),
                                            origin='measured',
                                            template=temp))
            meas.source = PerformedSource(record[self.performed_by_key],record[self.performed_date_key])
        # Measured properties of impact sample
        elif key in ['Sample Diameter','Sample Thickness'] :
            self.keys_used.append(key)
            if value=='' :
                return
            if self.impactsample is None :
                errmsg = f'ERROR: {key} measurement ({value}) found for a Launch Package with no impactsample!'
                self.logger.error(errmsg,ValueError)
            name=key.replace(' ','')
            meas = MeasurementRun(name=name,material=self.impactsample)
            temp = self.templates.attr(key)
            meas.properties.append(Property(name=name,
                                            value=NominalReal(float(value),temp.bounds.default_units),
                                            origin='measured',
                                            template=temp))
            meas.source = PerformedSource(record[self.performed_by_key],record[self.performed_date_key])
        else :
            super().add_other_key(key,value,record)

    def get_spec_kwargs(self,record) :
        kwargs = {}
        # the flyer stack, spacer ID, spacer cutting program, and sample that were used
        kwargs['flyerspec'] = self.flyerstack.spec if self.flyerstack is not None else None
        kwargs['spacerID'] = self.spacerID
        kwargs['spacercuttingname'] = self.spacercuttingname
        kwargs['spacercutting'] = self.spacercutting
        kwargs['spacercuttingenergy'] = record.pop('Spacer Cutting Energy')
        kwargs['spacercuttingnpasses_1'] = record.pop('Spacer Cut Num of Pass 1')
        kwargs['spacercuttingnpasses_2'] = record.pop('Spacer Cut Num of Pass 2')
        kwargs['spacercuttingnpasses_3'] = record.pop('Spacer Cut Num of Pass 3')
        kwargs['impactsamplespec'] = self.impactsample.spec if self.impactsample is not None else None
        # Choosing the Flyer from the stack
        kwargs['flyerrow']=record.pop('Flyer Row Location')
        kwargs['flyercol']=record.pop('Flyer Column Location')
        # Attaching spacer to flyer
        kwargs['use_spacer']=record.pop('Spacer Flag')=='Yes'
        kwargs['spacer_attachment']=record.pop('Spacer Attachment Method')
        kwargs['spacer_adhesive']=record.pop('Spacer Attachment Adhesive')
        # Attaching impact sample to flyer and spacer
        kwargs['use_sample']=record.pop('Sample Flag')=='Yes'
        kwargs['samp_attachments_adhesives']=record.pop('Sample Attachment Method').split('\r')
        kwargs['samp_orientation']=record.pop('Sample Impact Orientation')
        return kwargs

    #################### PRIVATE HELPER FUNCTIONS ####################

    def __get_impact_sample(self,record,templates,specs) :
        """
        Return an ImpactSample (piece of Sample that is cut and polished) given a FileMaker record
        """
        #pop all of the needed information from the record so it's used no matter what
        polish_pad = record.pop('Polishing Pad')
        sl = record.pop('Sample Location')
        slbo = record.pop('Sample Location based Order')
        polish_proc = (record.pop('Polishing Process')).rstrip() #extra space at the end of some values in the DB
        cutting_procs = record.pop('Cutting Procedures Used').split('\r')
        asym_polish = record.pop('Asymmetric Polish')
        polishing_side_2 = record.pop('Polishing Side 2')
        ns = ['Diamond Grit','Silicon Carbide Grit','Polishing Diamond Grit 2','Polishing Silicon Grit 2']
        vs = [record.pop(n) for n in ns]
        tns = ['Diamond Grit','Silicon Carbide Grit','Diamond Grit','Silicon Carbide Grit']
        #if there was no sample found, then there's no impact sample either
        if self.sample is None :
            return None
        #initial Spec
        params = []
        if polish_pad!='' :
            params.append(
                Parameter(name='Polishing Pad',
                          value=NominalCategorical(str(polish_pad)),
                          template=templates.attr('Polishing Pad'),
                          origin='specified')
            )
        if asym_polish=='' :
            asym_polish = 'No'
        params.append(
            Parameter(name='Asymmetric Polish',
                      value=NominalCategorical(str(asym_polish)),
                      template=templates.attr('Asymmetric Polish'),
                      origin='specified')
        )
        if asym_polish!='No' :
            params.append(
                Parameter(name='Polishing Side 2',
                          value=NominalCategorical(str(polishing_side_2)),
                          template=templates.attr('Polishing Side 2'),
                          origin='specified')
            )
        if sl!='' :
            params.append(
                Parameter(name='Sample Location',
                          value=NominalInteger(int(sl)),
                          template=templates.attr('Sample Location'),
                          origin='specified')
            )
        if slbo!='' :
            params.append(
                Parameter(name='Sample Location Based Order',
                          value=NominalInteger(int(slbo)),
                          template=templates.attr('Sample Location Based Order'),
                          origin='specified'),
            )
        conditions = []
        if polish_proc!='' :
            conditions.append(
                Condition(name='Polishing Process',
                          value=NominalCategorical(str(polish_proc)),
                          template=templates.attr('Polishing Process'),
                          origin='specified')
            )
        cutting_and_polishing = ProcessSpec(
                name='Impact Sample Cutting and Polishing',
                conditions=conditions,
                parameters=params,
                template=templates.obj('Impact Sample Cutting and Polishing'),
                )
        #add the cutting procedures as parameters of the process
        n = 'Impact Sample Cutting Procedure'
        for cp in cutting_procs :
            if cp=='' :
                continue
            cutting_and_polishing.conditions.append(Condition(name=n,
                                                                 value=NominalCategorical(str(cp)),
                                                                 template=templates.attr(n),
                                                                 origin='specified'))
        #add the polishing grit(s) as parameters of the process
        for n,v,tn in zip(ns,vs,tns) :
            if v!='' and v!='N/A':
                cutting_and_polishing.parameters.append(Parameter(name=n,
                                                                     value=NominalCategorical(str(v)),
                                                                     template=templates.attr(tn),
                                                                     origin='specified'))
        #add the sample as an ingredient in the process
        IngredientSpec(name='Sample',material=self.sample.spec,process=cutting_and_polishing)
        #define the material that is the impact sample
        MaterialSpec(
            name='Impact Sample',
            process=cutting_and_polishing,
            template=templates.obj('Impact Sample')
            )
        cutting_and_polishing = specs.unique_version_of(cutting_and_polishing)
        #create the Run from the Spec
        impactsample = make_instance(cutting_and_polishing.output_material)
        #add the sample to the Run
        for ing in impactsample.process.ingredients :
            if ing.name=='Sample' :
                ing.material=self.sample
        #return the ImpactSample Run
        return impactsample

    def __make_replacements(self,item) :
        if not isinstance_ingredient_run(item) :
            return
        if item.name=='Flyer Stack' :
            item.material = self.flyerstack
        elif item.name=='Spacer Material' :
            item.material = self.spacer
        elif item.name=='Impact Sample' :
            item.material = self.impactsample
