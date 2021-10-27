#imports
from hashlib import sha512
from gemd.entity.value import DiscreteCategorical, NominalReal
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter
from gemd.entity.object import ProcessSpec, MaterialSpec
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .laser_shock_spec import LaserShockSpec
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockGlassIDSpec(LaserShockSpec) :
    """
    General constructor for Glass ID Specs in the Laser Shock Lab
    """

    spec_type = MaterialSpec

    def __init__(self,*args,**kwargs) :
        self.supplier = kwargs.get('supplier')
        self.part_num = kwargs.get('part_num')
        self.thickness = kwargs.get('thickness')
        self.length = kwargs.get('length')
        self.width = kwargs.get('width')
        super().__init__(*args,**kwargs)

    def get_arg_hash(self) :
        arg_hash = sha512()
        arg_hash.update(self.supplier.encode())
        arg_hash.update(self.part_num.encode())
        arg_hash.update(str(self.thickness).encode())
        arg_hash.update(str(self.length).encode())
        arg_hash.update(str(self.width).encode())
        return arg_hash.hexdigest()

    def get_spec_kwargs(self) :
        spec_kwargs = {}
        #name
        spec_kwargs['name'] = 'Laser Shock Glass ID'
        #notes
        spec_kwargs['notes'] = 'One of the possible Specs for the glass pieces used in the Laser Shock Lab'
        #process
        spec_kwargs['process'] = ProcessSpec(
            name='Purchasing Glass',
            parameters=[
                Parameter(
                    name=ATTR_TEMPL['Glass Supplier'].name,
                    value=DiscreteCategorical({self.supplier:1.0}),
                    template=ATTR_TEMPL['Glass Supplier'],
                    origin='specified',
                    ),
                Parameter(
                    name=ATTR_TEMPL['Glass Part Number'].name,
                    value=DiscreteCategorical({self.part_num:1.0}),
                    template=ATTR_TEMPL['Glass Part Number'],
                    origin='specified',
                    ),
                ],
            template=OBJ_TEMPL['Purchasing Glass']
            )
        #properties
        spec_kwargs['properties']=[
            PropertyAndConditions(Property(
                name=ATTR_TEMPL['Glass Thickness'].name,
                value=NominalReal(self.thickness,
                                  ATTR_TEMPL['Glass Thickness'].bounds.default_units),
                template=ATTR_TEMPL['Glass Thickness'],
                origin='specified',
                )),
            PropertyAndConditions(Property(
                name=ATTR_TEMPL['Glass Length'].name,
                value=NominalReal(self.length,
                                  ATTR_TEMPL['Glass Length'].bounds.default_units),
                template=ATTR_TEMPL['Glass Length'],
                origin='specified',
                )),
            PropertyAndConditions(Property(
                name=ATTR_TEMPL['Glass Width'].name,
                value=NominalReal(self.width,ATTR_TEMPL['Glass Width'].bounds.default_units),
                template=ATTR_TEMPL['Glass Width'],
                origin='specified',
                )),
            ]
        #template
        spec_kwargs['template']=OBJ_TEMPL['Glass ID']
        return spec_kwargs

class LaserShockGlassID(MaterialRunFromFileMakerRecord) :
    """
    GEMD representation of a piece of glass in the Laser Shock Lab as a Material Run
    """

    spec_type = LaserShockGlassIDSpec

    name_key = 'Glass name'
    notes_key = 'Description'

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Glass ID']

    def ignore_key(self,key) :
        if key in ['Glass Picture'] :
            return True
        return super().ignore_key(key)

    def get_spec_kwargs(self,record) :
        kwargs = {}
        kwargs['supplier'] = record.pop('Glass Supplier')
        kwargs['part_num'] = record.pop('Glass Part Number')
        kwargs['thickness'] = record.pop('Glass Thickness')
        kwargs['length'] = record.pop('Glass Length')
        kwargs['width'] = record.pop('Glass Width')
        return kwargs
