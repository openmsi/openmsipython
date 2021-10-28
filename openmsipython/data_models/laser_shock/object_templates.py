#imports
from gemd.entity.template import MaterialTemplate, ProcessTemplate
#from gemd.entity.template import MeasurementTemplate
from .attribute_templates import ATTR_TEMPL

OBJ_TEMPL = {}

# Materials

name = 'Glass ID'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A piece of glass used in the Laser Shock Lab (used in creating Flyer Stacks)',
    properties = [ATTR_TEMPL['Glass Thickness'],
                  ATTR_TEMPL['Glass Length'],
                  ATTR_TEMPL['Glass Width'],
        ],
    )

name = 'Glass Epoxy Foil Stack'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A foil adhered to a piece of glass using an epoxy',
    )

name = 'Flyer Stack'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A set of flyer discs cut out of a glass/epoxy/foil stack',
    )

name = 'Raw Sample Material'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A raw material that is processed to produced a Laser Shock Sample',
    properties=[ATTR_TEMPL['Sample Material Processing'],
                ATTR_TEMPL['Sample Raw Material Composition'],
        ],
    )

name = 'Sample'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A Sample used in various Laser Shock experiments',
    properties=[ATTR_TEMPL['Density'],
                ATTR_TEMPL['Bulk Wave Speed'],
                ATTR_TEMPL['Average Grain Size']
        ],
    )

# Measurements

# Processes

name = 'Purchasing Glass'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Purchasing a piece of glass from a manufacturer',
    parameters=[ATTR_TEMPL['Glass Supplier'],
                ATTR_TEMPL['Glass Part Number'],
        ],
    allowed_names=[],
    )

name = 'Mixing Epoxy'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Mixing a two-part epoxy',
    parameters=[ATTR_TEMPL['Mixing Time'],
                ATTR_TEMPL['Resting Time'],
        ],
    )

name = 'Epoxying a Flyer Stack'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Adhering a foil to a piece of glass using an epoxy',
    conditions=[ATTR_TEMPL['Compression Method']],
    parameters=[ATTR_TEMPL['Compression Weight'],
                ATTR_TEMPL['Compression Time'],
        ],
    )

name = 'Cutting a Flyer Stack'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Cutting flyer discs out of a glass/epoxy/foil stack to make a Flyer Stack',
    parameters=[ATTR_TEMPL['Cutting Procedure'],
                ATTR_TEMPL['Flyer Spacing'],
                ATTR_TEMPL['Flyer Diameter'],
                ATTR_TEMPL['Rows X Columns']
        ]
    )

name = 'Sample Processing'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='''Processing a raw material of some type in some geometry, at some temperature,
                   and through some route to produce a Sample for the Laser Shock Lab''',
    conditions=[ATTR_TEMPL['Processing Geometry'],
                ATTR_TEMPL['Processing Temperature'],
        ],
    parameters=[
                ATTR_TEMPL['Processing Route'],
                ATTR_TEMPL['Processing Time'],
        ],
    )