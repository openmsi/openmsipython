#imports
import inspect
from gemd.entity.template import MaterialTemplate, ProcessTemplate, MeasurementTemplate
from .attribute_templates import ATTR_TEMPL

OBJ_TEMPL = {}

#################### MATERIALS ####################

name = 'Reactants'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='The reactants put into the furnace',
    properties = [ATTR_TEMPL['Reactant Formula'],
        ],
)

name = 'Products'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='The products from the furnace',
    properties = [ATTR_TEMPL['Product Formula'],
    ATTR_TEMPL['Sample Name'],
        ],
)

#################### MEASUREMENTS ####################

#################### PROCESSES ####################

name = 'Furnace'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Using the furnace on the reactants',
    parameters=[ATTR_TEMPL['Furnace Name'],
                ATTR_TEMPL['Zone Type'],
                ATTR_TEMPL['Temperature Profile'],
                ATTR_TEMPL['Timestamp'],
        ],
    allowed_names=[],
)



