#imports 
import copy
from gemd.entity.util import make_instance
from gemd.entity.source.performed_source import PerformedSource
from gemd.entity.value import DiscreteCategorical, NominalInteger, NominalReal
from gemd.entity.attribute import Property, Parameter, Condition
from gemd.entity.object import ProcessSpec, MaterialSpec, MeasurementSpec, MeasurementRun, IngredientSpec, IngredientRun
from .utilities import search_for_name, search_for_single_name, search_for_single_tag
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .laser_shock_spec_for_run import LaserShockSpecForRun
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockLaunchPackageSpec(LaserShockSpecForRun) :
    """
    Dynamically-created spec for a Launch Package
    """

    spec_type = MaterialSpec

    def __init__(self,*args,**kwargs) :
        self.flyerspec = kwargs.get('flyerspec')
        self.spacerID = kwargs.get('spacerID')
        self.spacercutting = kwargs.get('spacercutting')
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
        spec_kwargs['template'] = OBJ_TEMPL[spec_kwargs['name']]
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
                          template=ATTR_TEMPL['Flyer Row'],
                          origin='specified')
            )
        if self.flyercol!='' :
            choosing_flyer_params.append(
                Parameter(name='Flyer Column',
                          value=NominalInteger(int(self.flyercol)),
                          template=ATTR_TEMPL['Flyer Column'],
                          origin='specified')
            )
        choosing_flyer = ProcessSpec(
            name='Choosing Flyer',
            parameters=choosing_flyer_params,
            template=OBJ_TEMPL['Choosing Flyer'],
            )
        IngredientSpec(name='Flyer Stack',material=self.flyerspec,process=choosing_flyer)
        chosen_flyer = MaterialSpec(name='Chosen Flyer',process=choosing_flyer)
        # Create Spacer from Spacer ID and Spacer Cutting Program
        if not self.use_spacer :
            return choosing_flyer
        if self.spacercutting is not None :
            cutting_spacer = copy.copy(self.spacercutting)
        else :
            cutting_spacer = ProcessSpec(
                name='Cutting Spacer',
                template=OBJ_TEMPL['Cutting Spacer']
                )
        IngredientSpec(name='Spacer Material',material=self.spacerID,process=cutting_spacer)
        cut_spacer = MaterialSpec(name='Spacer',process=cutting_spacer)
        # Attach Spacer to Flyer
        attaching_spacer = ProcessSpec(
            name='Attaching Spacer',
            conditions=[
                Condition(name='Spacer Attachment Method',
                          value=DiscreteCategorical({self.spacer_attachment:1.0}),
                          template=ATTR_TEMPL['Spacer Attachment Method'],
                          origin='specified'),
                ],
            parameters=[
                Parameter(name='Spacer Adhesive',
                          value=DiscreteCategorical({self.spacer_adhesive:1.0}),
                          template=ATTR_TEMPL['Spacer Adhesive'],
                          origin='specified'),
                ],
            template=OBJ_TEMPL['Attaching Spacer']
            )
        IngredientSpec(name='Chosen Flyer',material=chosen_flyer,process=attaching_spacer)
        IngredientSpec(name='Spacer',material=cut_spacer,process=attaching_spacer)
        flyer_and_spacer = MaterialSpec(name='Flyer/Spacer',process=attaching_spacer)
        # Attach Impact Sample to Flyer/Spacer stack
        if not self.use_sample :
            return attaching_spacer
        attaching_sample = ProcessSpec(
            name='Attaching Sample',
            parameters=[
                Parameter(name='Sample Orientation',
                          value=DiscreteCategorical({self.samp_orientation:1.0}),
                          template=ATTR_TEMPL['Sample Orientation'],
                          origin='specified',
                    )
                ],
            template=OBJ_TEMPL['Attaching Sample']
            )
        for ai,a in enumerate(self.samp_attachments_adhesives) :
            if ai==0 :
                attaching_sample.conditions.append(
                    Condition(name='Sample Attachment Method',
                              value=DiscreteCategorical({a:1.0}),
                              template=ATTR_TEMPL['Sample Attachment Method'],
                              origin='specified')
                    )
            else :
                attaching_sample.parameters.append(
                    Parameter(name='Sample Attachment Adhesive',
                              value=DiscreteCategorical({a:1.0}),
                              template=ATTR_TEMPL['Sample Attachment Adhesive'],
                              origin='specified')
                    )
        IngredientSpec(name='Flyer/Spacer',material=flyer_and_spacer,process=attaching_sample)
        IngredientSpec(name='Impact Sample',material=self.impactsamplespec,process=attaching_sample)
        return attaching_sample

class LaserShockLaunchPackage(MaterialRunFromFileMakerRecord) :
    """
    A representation of a Launch Package in the Laser Shock Lab, created using a FileMaker record
    """

    spec_type = LaserShockLaunchPackageSpec

    name_key = 'Launch ID'
    performed_by_key = 'Performed By'
    performed_date_key = 'Date'

    def __init__(self,record,flyer_stacks,spacer_IDs,spacer_cutting_programs,samples) :
        # find the flyer stack, spacer ID, spacer cutting program, and sample that were used
        self.flyerstack = search_for_single_tag([fs.run for fs in flyer_stacks],'FlyerID',record.pop('Flyer ID').replace(' ','_'))
        self.spacerID = search_for_single_name([sid.spec for sid in spacer_IDs],record.pop('Spacer Type'))
        self.spacercutting = search_for_single_name([scp.spec for scp in spacer_cutting_programs],record.pop('Spacer Cutting Program'))
        self.sample = search_for_single_name([s.run for s in samples],record.pop('Sample Name'))
        # create Runs from Specs that were found
        self.spacer = make_instance(self.spacerID) if self.spacerID is not None else None
        # create the Impact Sample that was cut from the original sample
        self.impactsample = self.__get_impact_sample(record)
        # create the rest of the Run
        super().__init__(record)
        # link some objects back into the created Run
        for ing in self.run.process.ingredients :
            if ing.name=='Flyer/Spacer' :
                for ing2 in ing.material.process.ingredients :
                    if ing2.name=='Chosen Flyer' :
                        for ing3 in ing2.material.process.ingredients :
                            if ing3.name=='Flyer Stack' :
                                ing3.material=self.flyerstack
                    elif ing2.name=='Spacer' :
                        for ing3 in ing2.material.process.ingredients :
                            if ing3.name=='Spacer Material' :
                                ing3.material=self.spacer
            elif ing.name=='Impact Sample' :
                ing.material=self.impactsample

    @property
    def tags_keys(self):
        return [*super().tags_keys,'Secondary Sample ID']
    
    @property
    def other_keys(self) :
        return [*super().other_keys,
                'Spacer Inner Diameter','Spacer Outer Diameter',
                'Sample Diameter','Sample Thickness',
            ]

    def add_other_key(self,key,value,record) :
        # Measured properties of spacer
        if key in ['Spacer Inner Diameter','Spacer Outer Diameter'] :
            self.keys_used.append(key)
            if value=='' :
                return
            if self.spacer is None :
                errmsg = f'ERROR: {key} measurement ({value}) found for a Launch Package with no spacer!'
                raise ValueError(errmsg)
            name=key.replace(' ','')
            meas = MeasurementRun(name=name,material=self.spacer)
            meas.spec = MeasurementSpec(name=name)
            temp = ATTR_TEMPL['Spacer Diameter']
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
                raise ValueError(errmsg)
            name=key.replace(' ','')
            meas = MeasurementRun(name=name,material=self.impactsample)
            meas.spec = MeasurementSpec(name=name)
            temp = ATTR_TEMPL[key]
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
        kwargs['flyerspec'] = self.flyerstack.spec
        kwargs['spacerID'] = self.spacerID
        kwargs['spacercutting'] = self.spacercutting
        kwargs['impactsamplespec'] = self.impactsample.spec if self.impactsample is not None else None
        # Choosing the Flyer from the stack
        kwargs['flyerrow']=record.pop('Flyer Row Location')
        kwargs['flyercol']=record.pop('Flyer Column Location')
        # Attaching spacer to flyer
        kwargs['use_spacer']=record.pop('Spacer Flag')=='Yes'
        kwargs['spacer_attachment']=record.pop('Spacer Attachment Method')
        kwargs['spacer_adhesive']=record.pop('Spacer Attachment Adhesive')
        # Attaching impact sample to flyer/spacer
        kwargs['use_sample']=record.pop('Sample Flag')=='Yes'
        kwargs['samp_attachments_adhesives']=record.pop('Sample Attachment Method').split('\r')
        kwargs['samp_orientation']=record.pop('Sample Impact Orientation')
        return kwargs

    def __get_impact_sample(self,record) :
        """
        Return an ImpactSample (piece of Sample that is cut and polished) given a FileMaker record
        """
        #pop all of the needed information from the record so it's used no matter what
        polish_pad = record.pop('Polishing Pad')
        sl = record.pop('Sample Location')
        slbo = record.pop('Sample Location based Order')
        polish_proc = record.pop('Polishing Process')
        cutting_procs = record.pop('Cutting Procedures Used').split('\r')
        ns = ['Diamond Grit','Silicon Carbide Grit']
        vs = [record.pop(n) for n in ns]
        #if there was no sample found, then there's no impact sample either
        if self.sample is None :
            return None
        #initial Spec
        params = [
            Parameter(name='Polishing Pad',
                      value=DiscreteCategorical({polish_pad:1.0}),
                      template=ATTR_TEMPL['Polishing Pad'],
                      origin='specified')
        ]
        if sl!='' :
            params.append(
                Parameter(name='Sample Location',
                          value=NominalInteger(int(sl)),
                          template=ATTR_TEMPL['Sample Location'],
                          origin='specified')
            )
        if slbo!='' :
            params.append(
                Parameter(name='Sample Location Based Order',
                          value=NominalInteger(int(slbo)),
                          template=ATTR_TEMPL['Sample Location Based Order'],
                          origin='specified'),
            )
        impactsamplespec = MaterialSpec(
            name='Impact Sample',
            process=ProcessSpec(
                name='Impact Sample Cutting and Polishing',
                conditions=[
                    Condition(name='Polishing Process',
                              value=DiscreteCategorical({polish_proc:1.0}),
                              template=ATTR_TEMPL['Polishing Process'],
                              origin='specified')
                    ],
                parameters=params,
                template=OBJ_TEMPL['Impact Sample Cutting and Polishing'],
                ),
            template=OBJ_TEMPL['Impact Sample']
            )
        #add the cutting procedures as parameters of the process
        n = 'Impact Sample Cutting Procedure'
        for cp in cutting_procs :
            impactsamplespec.process.conditions.append(Condition(name=n,
                                                                 value=DiscreteCategorical({cp:1.0}),
                                                                 template=ATTR_TEMPL[n],
                                                                 origin='specified'))
        #add the polishing grit(s) as parameters of the process
        for n,v in zip(ns,vs) :
            if v!='' and v!='N/A':
                impactsamplespec.process.parameters.append(Parameter(name=n,
                                                                     value=DiscreteCategorical({v:1.0}),
                                                                     template=ATTR_TEMPL[n],
                                                                     origin='specified'))
        #add the sample as an ingredient in the process
        IngredientSpec(name='Sample',material=self.sample.spec,process=impactsamplespec.process)
        #create the Run from the Spec
        impactsample = make_instance(impactsamplespec)
        #add the sample to the Run
        IngredientRun(material=self.sample,process=impactsample.process)
        #return the ImpactSample Run
        return impactsample
