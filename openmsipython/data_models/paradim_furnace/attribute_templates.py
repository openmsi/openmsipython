#imports
import inspect
from gemd import EmpiricalFormula
from gemd.entity.bounds import IntegerBounds, RealBounds, CategoricalBounds, CompositionBounds
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate

ATTR_TEMPL = {}

#################### PROPERTIES ####################

name = 'Sample Name'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The name of the sample',
    bounds=CategoricalBounds(['?????'])
)

name = 'Reactants'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The reactants put into the furnace',
    bounds=CompositionBounds(components=EmpiricalFormula.all_elements)
)

name = 'Products'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The products of the furnace',
    bounds=CompositionBounds(components=EmpiricalFormula.all_elements)
)


#################### PARAMETERS ####################

name = 'Furnace Name'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The name of the furnace the reaction is occuring in',
    bounds=CategoricalBounds(['Kilgore', 'Challenger', 'Frank', 'Bodie']),
)

name = 'Zone Type'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description="The manufacturer's part number for a piece of glass that was purchased",
    bounds=CategoricalBounds(['Single Zone','Three Zone']),
)

name = 'Furnace Temperature Profile'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The temperature profile of the furnace',
    bounds=CategoricalBounds(['?????']),
)

#################### CONDITIONS ####################

name = 'Timestamp'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The time and date that the form was filled out',
    bounds=CategoricalBounds(['????????'])
)

