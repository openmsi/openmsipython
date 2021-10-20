#imports
from gemd.entity.template import MaterialTemplate, ProcessTemplate
#from gemd.entity.template import MeasurementTemplate
from .attribute_templates import ATTR_TEMPL

OBJ_TEMPL = {}

# Materials

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

name = 'Purchasing'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Purchasing a material from a manufacturer',
    allowed_names=[], # Not allowed to have any ingredients
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
        ],
    )