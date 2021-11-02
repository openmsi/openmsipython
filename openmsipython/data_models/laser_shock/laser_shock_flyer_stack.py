#imports
import copy, sha512
from gemd.entity.util import make_instance
from gemd.entity.source import PerformedSource
from gemd.entity.value import DiscreteCategorical, NominalInteger, NominalReal
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter, Condition
from gemd.entity.object import ProcessSpec, MaterialSpec, MeasurementSpec, MeasurementRun, IngredientSpec
from .utilities import search_for_single_name
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .laser_shock_spec_for_run import LaserShockSpecForRun
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockFlyerStackSpec(LaserShockSpecForRun) :
    """
    The Spec for a given Flyer Stack
    """

    def __init__(self,*args,**kwargs) :
        self.glassID = kwargs.get('glassID')
        self.foilID = kwargs.get('foilID')
        self.epoxyID = kwargs.get('epoxyID')
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
        super().__init__(*args,**kwargs)

    def get_arg_hash(self) :
        arg_hash = sha512()
        if self.glassID is not None :
            arg_hash.update(self.glassID.name.encode())
        if self.foilID is not None :
            arg_hash.update(self.foilID.name.encode())
        if self.epoxyID is not None :
            arg_hash.update(self.epoxyID.name.encode())
        if self.cutting is not None :
            arg_hash.update(self.cutting.name.encode())
        arg_hash.update(self.part_a.encode())
        arg_hash.update(self.part_b.encode())
        arg_hash.update(self.mixing_time.encode())
        arg_hash.update(self.resting_time.encode())
        arg_hash.update(self.comp_method.encode())
        arg_hash.update(self.comp_weight.encode())
        arg_hash.update(self.comp_time.encode())
        arg_hash.update(self.s.encode())
        arg_hash.update(self.d.encode())
        arg_hash.update(self.n.encode())
        return arg_hash.hexdigest()

    def get_spec_kwargs(self) :
        spec_kwargs = {}
        #name
        spec_kwargs['name'] = 'Flyer Stack' if self.cutting is not None else 'Glass Epoxy Foil Stack'
        #notes
        if self.cutting is not None :
            spec_kwargs['notes'] = 'A spec for creating a set of flyer discs cut out from a glass/epoxy/foil stack'
        else :
            spec_kwargs['notes'] = 'A spec for creating a glass/epoxy/foil stack'
        #process
        spec_kwargs['process'] = self.__get_process()
        #the template
        spec_kwargs['template'] = OBJ_TEMPL[spec_kwargs['name']]
        return spec_kwargs

    def __get_process(self) :
        """
        Helper function to return the process spec for this Flyer Stack spec
        """
        #process, materials, and ingredients for mixing epoxy
        mixing_epoxy = ProcessSpec(
            name='Mixing Epoxy',
            parameters=[
                Parameter(
                    name='Mixing Time',
                    value=NominalInteger(int(self.mixing_time.split(':')[0])), # assume an int # of mins like 05:00:00
                    template=ATTR_TEMPL['Mixing Time'],
                    origin='specified',
                    ),
                Parameter(
                    name='Resting Time',
                    value=NominalInteger(int(self.resting_time.split(':')[0])), # ^ same with resting time
                    template=ATTR_TEMPL['Resting Time'],
                    origin='specified',
                    ),
                ],
            template=OBJ_TEMPL['Mixing Epoxy']
            )
        epoxy_part_a = MaterialSpec(name='Epoxy Part A',
                                    process=self.epoxyID.process if self.epoxyID is not None else None)
        epoxy_part_b = MaterialSpec(name='Epoxy Part B',
                                    process=self.epoxyID.process if self.epoxyID is not None else None)
        IngredientSpec(name='Epoxy Part A',material=epoxy_part_a,process=mixing_epoxy,
                       absolute_quantity=NominalReal(float(self.part_a),'g'))
        IngredientSpec(name='Epoxy Part B',material=epoxy_part_b,process=mixing_epoxy,
                       absolute_quantity=NominalReal(float(self.part_b),'g'))
        #process and ingredients for making the glass/epoxy/foil stack
        epoxying = ProcessSpec(
            name='Epoxying a Flyer Stack',
            conditions=[
                Condition(
                    name='Compression Method',
                    value=DiscreteCategorical({self.comp_method:1.0}),
                    template=ATTR_TEMPL['Compression Method'],
                    origin='specified',
                    )
                ],
            parameters=[
                Parameter(
                    name='Compression Weight',
                    value=NominalReal(float(self.comp_weight),'lb'),
                    template=ATTR_TEMPL['Compression Weight'],
                    origin='specified',
                    ),
                Parameter(
                    name='Compression Time',
                    value=NominalReal(float(self.comp_time),'hr'),
                    template=ATTR_TEMPL['Compression Time'],
                    origin='specified',
                    ),
                ],
            template=OBJ_TEMPL['Epoxying a Flyer Stack'],
            )
        IngredientSpec(name='Glass ID',material=self.glassID if self.glassID is not None else None,process=epoxying)
        IngredientSpec(name='Foil ID',material=self.foilID if self.foilID is not None else None,process=epoxying)
        IngredientSpec(name='Epoxy mixture',material=mixing_epoxy.output_material,process=epoxying)
        #process and ingredients for cutting flyer discs into the glass/epoxy/foil stack
        if self.cutting is not None :
            cutting = copy.copy(self.cutting)
        else :
            cutting = ProcessSpec(name='Cutting Flyer Discs')
        cutting.parameters.append(
            Parameter(
                name='Flyer Spacing',
                value=NominalReal(float(self.s),'mm'),
                template=ATTR_TEMPL['Flyer Spacing'],
                origin='specified',
                )
            )
        cutting.parameters.append(
            Parameter(
                name='Flyer Diameter',
                value=NominalReal(float(self.d),'mm'),
                template=ATTR_TEMPL['Flyer Diameter'],
                origin='specified',
                )
            )
        cutting.parameters.append(
            Parameter(
                name='Rows X Columns',
                value=NominalInteger(float(self.n)),
                template=ATTR_TEMPL['Rows X Columns'],
                origin='specified',
                )
            )
        IngredientSpec(name='Glass Epoxy Foil Stack',material=epoxying.output_material,process=cutting)
        return cutting

class LaserShockFlyerStack(MaterialRunFromFileMakerRecord) :
    """
    A Flyer Stack created from a piece of glass, a foil, and an epoxy, cut using a Flyer Cutting program
    """

    notes_key = 'Flyer Stack Note'
    performed_by_key = 'Performed By'
    performed_date_key = 'Date'

    def __init__(self,record,specs,glass_IDs,foil_IDs,epoxy_IDs,flyer_cutting_programs) :
        #find the glass, foil, epoxy, and flyer cutting program that were used for this run
        self.glassID = search_for_single_name(glass_IDs,record.pop('Glass Name Reference'))
        self.foilID = search_for_single_name(foil_IDs,record.pop('Foil Name'))
        self.epoxyID = search_for_single_name(epoxy_IDs,record.pop('Epoxy Name'))
        self.cutting = search_for_single_name(flyer_cutting_programs,record.pop('Cutting Procedure Name'))
        #create Runs from the Specs found
        self.glass = make_instance(self.glassID) if self.glassID is not None else None
        self.foil = make_instance(self.foilID) if self.foilID is not None else None
        self.epoxy = make_instance(self.epoxyID) if self.epoxyID is not None else None
        #run the rest of the creating the MaterialRun
        super().__init__(record,specs)
        #add the runs from above to each part of the created Run as necessary
        for ing in self.run.process.ingredients :
            if ing.name=='Glass Epoxy Foil Stack' :
                for ing2 in ing.material.process.ingredients :
                    if ing2.name=='Glass ID' :
                        ing2.material=self.glass
                    elif ing2.name=='Foil ID' :
                        ing2.material=self.foil
                    elif ing2.name=='Epoxy mixture' :
                        self.epoxy.process=ing2.material.process
                        ing2.material=self.epoxy

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Flyer ID']

    @property
    def ignore_key(self,key) :
        #I don't have access to the "Flyer Epoxy Thickness" calculated box through the API 
        #so I'm going to ignore the associated "Row Number" and "Column Number" fields for now 
        if key in ['Row Number','Column Number'] :
            return True
        return super().ignore_key(key)

    @property
    def measured_property_dict(self) :
        rd = {}
        for i in range(1,5) :
            rd[f'Stack Thickness {i}'] = {'valuetype':NominalReal,
                                          'datatype':float,
                                          'template':ATTR_TEMPL['Stack Thickness']}
        return rd

    @property
    def other_keys(self) :
        return [*super().other_keys,
                *[f'Glass Thickness {i}' for i in range(1,5)],'Glass width','Glass length',
                *[f'Foil Thickness {i}' for i in range(1,5)],
                *[f'Epoxy Thickness {i}' for i in range(1,5)],
                self.performed_date_key,
               ]

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
            meas.spec = MeasurementSpec(name=name)
            temp = None
            if key.startswith('Glass Thickness') :
                temp = ATTR_TEMPL['Glass Thickness mm']
            elif key=='Glass width' :
                temp = ATTR_TEMPL['Glass Width mm']
            elif key=='Glass length' :
                temp = ATTR_TEMPL['Glass Length mm']
            meas.properties.append(Property(name=name,
                                            value=NominalReal(float(value),temp.bounds.default_units),
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
            meas.spec = MeasurementSpec(name=name)
            temp = ATTR_TEMPL['Foil Thickness']
            meas.properties.append(Property(name=name,
                                            value=NominalReal(float(value),temp.bounds.default_units),
                                            origin='measured',
                                            template=temp))
            meas.source = PerformedSource(record[self.performed_by_key],record[self.performed_date_key])
        # Calculated properties of the Flyer Stack
        elif key.startswith('Epoxy Thickness') :
            self.keys_used.append(key)
            if value=='' :
                return
            if self.epoxy is None :
                errmsg = f'ERROR: {key} calculation ({value}) found for a Flyer Stack with no recognized epoxy object!'
                raise ValueError(errmsg)
            name=key.replace(' ','')
            temp = ATTR_TEMPL['Epoxy Thickness']
            self.epoxy.properties.append(PropertyAndConditions(Property(
                name=name,
                value=NominalReal(float(value),temp.bounds.default_units),
                origin='calculated',
                template=temp)))
        else :
            super().add_other_key(key,value,record)

    def get_spec_kwargs(self,record) :
        kwargs = {}
        # The other materials/processes that were used/performed
        kwargs['glassID'] = self.glassID
        kwargs['foilID'] = self.foilID
        kwargs['epoxyID'] = self.epoxyID
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
        return kwargs
