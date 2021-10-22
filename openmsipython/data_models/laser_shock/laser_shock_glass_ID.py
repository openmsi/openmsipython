#imports
from hashlib import sha512
from gemd.entity.value import DiscreteCategorical, NominalReal
from gemd.entity.attribute import PropertyAndConditions, Property, Parameter
from gemd.entity.object import ProcessSpec, MaterialSpec
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockGlassIDSpec :
    """
    General constructor for Glass ID Specs in the Laser Shock Lab
    """

    def __init__(self,supplier,part_num,thickness,length,width) :
        #save the arguments
        self.args = [supplier,part_num,thickness,length,width]
        #create the unique Spec name as a hash of the arguments
        name_hash = sha512()
        name_hash.update('Laser Shock Glass ID'.encode())
        name_hash.update(supplier.encode())
        name_hash.update(part_num.encode())
        name_hash.update(str(thickness).encode())
        name_hash.update(str(length).encode())
        name_hash.update(str(width).encode())
        name = name_hash.hexdigest()
        #notes
        notes = 'One of the possible Specs for the glass pieces used in the Laser Shock Lab'
        #define other arguments to the MaterialSpec
        process = ProcessSpec(
            name=name,
            parameters=[
                Parameter(
                    name=ATTR_TEMPL['Glass Supplier'].name,
                    value=DiscreteCategorical({supplier:1.0}),
                    template=ATTR_TEMPL['Glass Supplier'],
                    origin='specified',
                    ),
                Parameter(
                    name=ATTR_TEMPL['Glass Part Number'].name,
                    value=DiscreteCategorical({part_num:1.0}),
                    template=ATTR_TEMPL['Glass Part Number'],
                    origin='specified',
                    ),
                ],
            )
        properties=[
            PropertyAndConditions(Property(
                name=ATTR_TEMPL['Glass Thickness'].name,
                value=NominalReal(thickness,ATTR_TEMPL['Glass Thickness'].bounds.default_units),
                template=ATTR_TEMPL['Glass Thickness'],
                origin='specified',
                )),
            PropertyAndConditions(Property(
                name=ATTR_TEMPL['Glass Length'].name,
                value=NominalReal(length,ATTR_TEMPL['Glass Length'].bounds.default_units),
                template=ATTR_TEMPL['Glass Length'],
                origin='specified',
                )),
            PropertyAndConditions(Property(
                name=ATTR_TEMPL['Glass Width'].name,
                value=NominalReal(width,ATTR_TEMPL['Glass Width'].bounds.default_units),
                template=ATTR_TEMPL['Glass Width'],
                origin='specified',
                )),
            ]
        #actually create the MaterialSpec
        self.spec=MaterialSpec(name=name,notes=notes,
                               process=process,properties=properties,template=OBJ_TEMPL['Purchasing Glass'])

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

    def get_spec_args(self,record) :
        args = []
        args.append(record.pop('Glass Supplier'))
        args.append(record.pop('Glass Part Number'))
        args.append(record.pop('Glass Thickness'))
        args.append(record.pop('Glass Length'))
        args.append(record.pop('Glass Width'))
        return args
