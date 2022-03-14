#imports
import copy
from gemd.util.impl import recursive_foreach
from gemd.entity.util import make_instance
from gemd.entity.source.performed_source import PerformedSource
from gemd.entity.value import NominalCategorical, NominalInteger, NominalReal
from gemd.entity.attribute import Property, Parameter, Condition
from gemd.entity.object import ProcessSpec, MaterialSpec, MeasurementSpec, MeasurementRun, IngredientSpec
from ..utilities import search_for_single_name
from ..cached_isinstance_functions import isinstance_ingredient_run
from ..spec_for_run import SpecForRun
from ..run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockFlyerStackSpec(SpecForRun) :
    """
    The Spec for a given Flyer Stack
    """

    spec_type = MaterialSpec

    def __init__(self,*args,**kwargs) :
        self.glassID = kwargs.get('glassID')
        self.foilID = kwargs.get('foilID')
        self.epoxyID = kwargs.get('epoxyID')
        self.cutting_proc_name = kwargs.get('cutting_proc_name')
        self.cutting = kwargs.get('cutting')
        self.part_a = kwargs.get('part_a')
        self.part_b = kwargs.get('part_b')
        self.mixing_time = kwargs.get('mixing_time')
        self.resting_time = kwargs.get('resting_time')
        self.comp_method = kwargs.get('comp_method')
        self.comp_weight = kwargs.get('comp_weight')
        self.comp_time = kwargs.get('comp_time')
        self.s = kwargs.get('s')
        self.d = kwargs.get('d')
        self.n = kwargs.get('n')
        self.cutting_energy = kwargs.get('cutting_energy')
        self.n_passes = kwargs.get('n_passes')
        self.logger = kwargs.get('logger')
        super().__init__(*args,**kwargs)

    def get_spec_kwargs(self) :
        spec_kwargs = {}
        #name
        spec_kwargs['name'] = 'Flyer Stack'
        #notes
        if self.cutting is not None :
            spec_kwargs['notes'] = 'A spec for creating a set of flyer discs cut out from a glass/epoxy/foil stack'
        else :
            spec_kwargs['notes'] = 'A spec for creating a glass/epoxy/foil stack'
        #process
        spec_kwargs['process'] = self.__get_process()
        #the template
        spec_kwargs['template'] = self.templates.obj(spec_kwargs['name'])
        return spec_kwargs

    def __get_process(self) :
        """
        Helper function to return the process spec for this Flyer Stack spec
        """
        #process, materials, and ingredients for mixing epoxy
        mixing_epoxy_params = []
        if self.mixing_time!='' :
            if type(self.mixing_time)==str :
                val = int(self.mixing_time.split(':')[0]) # assume an int # of mins like 05:00:00
            elif type(self.mixing_time)==int :
                val = self.mixing_time
            else :
                self.logger.error(f'ERROR: receivied a mixing time value of type {type(self.mixing_time)}',TypeError)
            mixing_epoxy_params.append(
                Parameter(
                    name='Mixing Time',
                    value=NominalInteger(val), 
                    template=self.templates.attr('Mixing Time'),
                    origin='specified',
                    )
            )
        if self.resting_time!='' :
            if type(self.resting_time)==str :
                val = int(self.resting_time.split(':')[0]) # ^ same with resting time
            elif type(self.resting_time)==int :
                val = self.resting_time
            else :
                self.logger.error(f'ERROR: receivied a resting time value of type {type(self.resting_time)}',TypeError)
            mixing_epoxy_params.append(
                Parameter(
                    name='Resting Time',
                    value=NominalInteger(val), 
                    template=self.templates.attr('Resting Time'),
                    origin='specified',
                    )
            )
        mixing_epoxy = ProcessSpec(
            name='Mixing Epoxy',
            parameters=mixing_epoxy_params,
            template=self.templates.obj('Mixing Epoxy')
            )
        aq = NominalReal(float(self.part_a),'g') if self.part_a!='' else None
        IngredientSpec(name='Epoxy Part A',material=self.epoxyID if self.epoxyID is not None else None,
                                 process=mixing_epoxy,absolute_quantity=aq)
        aq = NominalReal(float(self.part_b),'g') if self.part_b!='' else None
        IngredientSpec(name='Epoxy Part B',material=self.epoxyID if self.epoxyID is not None else None,
                                 process=mixing_epoxy,absolute_quantity=aq)
        MaterialSpec(name='Mixed Epoxy',process=mixing_epoxy)
        mixing_epoxy = self.specs.unique_version_of(mixing_epoxy)
        #process and ingredients for making the glass/epoxy/foil stack
        epoxying_conds = []
        if self.comp_method!='' :
            epoxying_conds.append(
                Condition(
                    name='Compression Method',
                    value=NominalCategorical(str(self.comp_method)),
                    template=self.templates.attr('Compression Method'),
                    origin='specified',
                    )
            )
        epoxying_params = []
        if self.comp_weight!='' :
            epoxying_params.append(
                Parameter(
                    name='Compression Weight',
                    value=NominalReal(float(self.comp_weight),'lb'),
                    template=self.templates.attr('Compression Weight'),
                    origin='specified',
                    )
            )
        if self.comp_time!='' :
            epoxying_params.append(
                Parameter(
                    name='Compression Time',
                    value=NominalReal(float(self.comp_time),'hr'),
                    template=self.templates.attr('Compression Time'),
                    origin='specified',
                    )
            )
        epoxying = ProcessSpec(
            name='Epoxying a Flyer Stack',
            conditions=epoxying_conds,
            parameters=epoxying_params,
            template=self.templates.obj('Epoxying a Flyer Stack'),
            )
        IngredientSpec(name='Glass ID',material=self.glassID if self.glassID is not None else None,process=epoxying)
        IngredientSpec(name='Foil ID',material=self.foilID if self.foilID is not None else None,process=epoxying)
        IngredientSpec(name='Mixed Epoxy',material=mixing_epoxy.output_material,process=epoxying)
        MaterialSpec(name='Glass Epoxy Foil Stack',process=epoxying)
        epoxying = self.specs.unique_version_of(epoxying)
        #process and ingredients for cutting flyer discs into the glass/epoxy/foil stack
        if self.cutting is not None :
            cutting = copy.deepcopy(self.cutting)
            if self.specs.encoder.scope in cutting.uids.keys() :
                _ = cutting.uids.pop(self.specs.encoder.scope)
        else :
            new_cutting_proc_name = self.cutting_proc_name if self.cutting_proc_name!='' else 'Generic Flyer Cutting'
            cutting = ProcessSpec(name=new_cutting_proc_name,template=self.templates.obj('Flyer Cutting Program'))
        if self.s!='' :
            cutting.parameters.append(
                Parameter(
                    name='Flyer Spacing',
                    value=NominalReal(float(self.s),'mm'),
                    template=self.templates.attr('Flyer Spacing'),
                    origin='specified',
                    )
                )
        if self.d!='' :
            cutting.parameters.append(
                Parameter(
                    name='Flyer Diameter',
                    value=NominalReal(float(self.d),'mm'),
                    template=self.templates.attr('Flyer Diameter'),
                    origin='specified',
                    )
                )
        if self.n!='' :
            cutting.parameters.append(
                Parameter(
                    name='Rows X Columns',
                    value=NominalInteger(float(self.n)),
                    template=self.templates.attr('Rows X Columns'),
                    origin='specified',
                    )
                )
        if self.cutting_energy!='' :
            temp = self.templates.attr('Laser Cutting Energy')
            laser_cutting_energy_par = None
            for p in cutting.parameters :
                if p.name=='LaserCuttingEnergy' :
                    laser_cutting_energy_par = p
                    break
            if laser_cutting_energy_par is not None :
                new_value=NominalReal(float(self.cutting_energy),temp.bounds.default_units)
                #msg =  'WARNING: replacing laser cutting energy in a created Spec based on new information in the '
                #msg+= f'Flyer Stack layout. Old value = {p.value}, new value = {new_value}'
                #self.logger.warning(msg)
                p.value=new_value
            else :
                cutting.parameters.append(
                    Parameter(
                        name='LaserCuttingEnergy',
                        value=NominalReal(float(self.cutting_energy),temp.bounds.default_units),
                        template=temp,
                        origin='specified',
                        )
                )
        if self.n_passes!='' :
            n_passes_par = None
            for p in cutting.parameters :
                if p.name=='NumberofPasses' :
                    n_passes_par = p
                    break
            if n_passes_par is not None :
                new_value=NominalInteger(int(self.n_passes))
                #msg =  'WARNING: replacing number of passes in a created Spec based on new information in the '
                #msg+= f'Flyer Stack layout. Old value = {p.value}, new value = {new_value}'
                #self.logger.warning(msg)
                p.value=new_value
            else :
                cutting.parameters.append(
                    Parameter(
                        name='NumberofPasses',
                        value=NominalInteger(int(self.n_passes)),
                        template=self.templates.attr('Number of Passes'),
                        origin='specified',
                        )
                )
        IngredientSpec(name='Glass Epoxy Foil Stack',material=epoxying.output_material,process=cutting)
        cutting = self.specs.unique_version_of(cutting)
        return cutting

class LaserShockFlyerStack(MaterialRunFromFileMakerRecord) :
    """
    A Flyer Stack created from a piece of glass, a foil, and an epoxy, cut using a Flyer Cutting program
    """

    spec_type = LaserShockFlyerStackSpec

    notes_key = 'Flyer Stack Note'
    performed_by_key = 'Performed By'
    performed_date_key = 'Date'

    #################### PROPERTIES ####################

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Flyer ID']

    @property
    def measured_property_dict(self) :
        rd = {}
        for i in range(1,5) :
            rd[f'Stack Thickness {i}'] = {'valuetype':NominalReal,
                                          'datatype':float,
                                          'template':self.templates.attr('Stack Thickness')}
            rd[f'Epoxy Thickness {i}'] = {'valuetype':NominalReal,
                                          'datatype':float,
                                          'template':self.templates.attr('Epoxy Thickness'),
                                          'origin':'computed'}
        rd['Time to Cut'] = {'valuetype':NominalReal,
                             'datatype':float,
                             'template':self.templates.attr('Time To Cut')}
        rd['Flyer Cutting Depth Success'] = {'valuetype':NominalCategorical,
                                             'template':self.templates.attr('Flyer Cutting Depth Success')}
        rd['Flyer Cutting Completeness'] = {'valuetype':NominalInteger,
                                            'datatype':int,
                                            'template':self.templates.attr('Flyer Cutting Completeness')}
        return rd

    @property
    def other_keys(self) :
        return [*super().other_keys,
                *[f'Glass Thickness {i}' for i in range(1,5)],'Glass width','Glass length',
                *[f'Foil Thickness {i}' for i in range(1,5)],
                self.performed_date_key,
               ]

    @property
    def unique_values(self):
        flyer_ID_tags = [t for t in self.run.tags if t.startswith('FlyerID')]
        if len(flyer_ID_tags)!=1 :
            errmsg = f'ERROR: found {len(flyer_ID_tags)} tags specifying a Flyer ID when there should be exactly one'
            self.logger.error(errmsg,RuntimeError)
        return {**super().unique_values,'Flyer ID':flyer_ID_tags[0]}

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,record,glass_IDs,foil_IDs,epoxy_IDs,flyer_cutting_programs,**kwargs) :
        #set the logger until it can be overwritten after everything else is initialized
        self.logger = kwargs.get('logger')
        #find the glass, foil, epoxy, and flyer cutting program that were used for this run
        self.glassID = search_for_single_name([gid for gid in glass_IDs],
                                              record.pop('Glass Name Reference'),logger=kwargs.get('logger'))
        self.foilID = search_for_single_name([fid for fid in foil_IDs],
                                             record.pop('Foil Name'),logger=kwargs.get('logger'))
        self.epoxyID = search_for_single_name([eid for eid in epoxy_IDs],
                                              record.pop('Epoxy Name'),logger=kwargs.get('logger'))
        self.cutting_procedure_name = record.pop('Cutting Procedure Name')
        self.cutting = search_for_single_name([fcp for fcp in flyer_cutting_programs],
                                              self.cutting_procedure_name,logger=kwargs.get('logger'))
        #create Runs from the Specs found
        self.glass = make_instance(self.glassID) if self.glassID is not None else None
        self.foil = make_instance(self.foilID) if self.foilID is not None else None
        #run the rest of the creating the MaterialRun
        super().__init__(record,**kwargs)
        #add the runs from above to each part of the created Run as necessary
        recursive_foreach(self.run.process.ingredients,self.__make_replacements,apply_first=True)

    def ignore_key(self,key) :
        #I don't have access to the "Flyer Epoxy Thickness" calculated box through the API 
        #so I'm going to ignore the associated "Row Number" and "Column Number" fields for now 
        if key in ['Row Number','Column Number'] :
            return True
        return super().ignore_key(key)

    def add_other_key(self,key,value,record) :
        # Measured properties of the Glass run
        if key.startswith('Glass Thickness') or key in ['Glass width','Glass length'] :
            self.keys_used.append(key)
            if value=='' :
                return
            if self.glass is None :
                errmsg = f'ERROR: {key} measurement ({value}) found for a Flyer Stack with no recognized glass object!'
                raise ValueError(errmsg)
            name=key.replace(' ','')
            meas = MeasurementRun(name=name,material=self.glass)
            temp = None
            if key.startswith('Glass Thickness') :
                temp = self.templates.attr('Glass Thickness')
            elif key=='Glass width' :
                temp = self.templates.attr('Glass Width')
            elif key=='Glass length' :
                temp = self.templates.attr('Glass Length')
            meas.properties.append(Property(name=name,
                                            value=NominalReal(float(value),'mm'),
                                            origin='measured',
                                            template=temp))
            meas.source = PerformedSource(record[self.performed_by_key],record[self.performed_date_key])
        # Measured properties of the foil run
        elif key.startswith('Foil Thickness') :
            self.keys_used.append(key)
            if value=='' :
                return
            if self.foil is None :
                errmsg = f'ERROR: {key} measurement ({value}) found for a Flyer Stack with no recognized foil object!'
                raise ValueError(errmsg)
            name=key.replace(' ','')
            meas = MeasurementRun(name=name,material=self.foil)
            temp = self.templates.attr('Foil Thickness')
            meas.properties.append(Property(name=name,
                                            value=NominalReal(float(value),temp.bounds.default_units),
                                            origin='measured',
                                            template=temp))
            meas.source = PerformedSource(record[self.performed_by_key],record[self.performed_date_key])
        else :
            super().add_other_key(key,value,record)

    def get_spec_kwargs(self,record) :
        kwargs = {}
        # The other materials/processes that were used/performed
        kwargs['glassID'] = self.glassID
        kwargs['foilID'] = self.foilID
        kwargs['epoxyID'] = self.epoxyID
        kwargs['cutting_proc_name'] = self.cutting_procedure_name
        kwargs['cutting'] = self.cutting
        # Ingredients/Parameters for mixing epoxy
        kwargs['part_a'] = record.pop('Part A')
        kwargs['part_b'] = record.pop('Part B')
        kwargs['mixing_time'] = record.pop('Mixing Time')
        kwargs['resting_time'] = record.pop('Resting Time')
        # Parameters for making the glass/epoxy/foil stack
        kwargs['comp_method'] = record.pop('Compression Method')
        kwargs['comp_weight'] = record.pop('Compression Weight')
        kwargs['comp_time'] = record.pop('Compression Time')
        # Parameters of the Flyer Cutting procedure
        kwargs['s'] = record.pop('Flyer Spacing')
        kwargs['d'] = record.pop('Flyer Diameter')
        kwargs['n'] = record.pop('Rows X Columns')
        kwargs['cutting_energy'] = record.pop('Cutting Energy')
        kwargs['n_passes'] = record.pop('Number of Passes')
        # The logger (creating the Spec might throw some warnings)
        kwargs['logger'] = self.logger
        return kwargs

    #################### PRIVATE HELPER FUNCTIONS ####################

    def __make_replacements(self,item) :
        if not isinstance_ingredient_run(item) :
            return
        if item.name=='Glass ID' :
            item.material = self.glass
        elif item.name=='Foil ID' :
            item.material = self.foil
