#imports
from gemd.entity.bounds import RealBounds, CategoricalBounds, CompositionBounds
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate

ATTR_TEMPL = {}

# Properties

name = 'Glass Thickness'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The thickness of a piece of glass',
    bounds=RealBounds(0,2,'in')
    )

name = 'Glass Length'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The length of a piece of glass',
    bounds=RealBounds(0,12,'in')
    )

name = 'Glass Width'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The width of a piece of glass',
    bounds=RealBounds(0,12,'in')
    )

name = 'Sample Material Processing'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='Possible values in the "Material Processing" menu buttons in the "Sample" layout',
    bounds=CategoricalBounds(['Metal','Ceramic','Polymer','BMG','HEA','Composite'])
    )

name = 'Sample Raw Material Composition'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description="The composition of a raw material that's processed to produce a Laser Shock Sample",
    bounds=CompositionBounds(components=('Mg','Al','Zr','Ti','Cu','Ni','Be'))
    )

name = 'Density'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The density of something',
    bounds=RealBounds(0,20e3,'kg/m^3'),
    )

name = 'Bulk Wave Speed'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The speed at which waves propagate through a material',
    bounds=RealBounds(0,36e3,'m/s'),
    )

name = 'Average Grain Size'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The average size of grains in a material',
    bounds=RealBounds(0,1e3,'um')
    )


# Parameters

name = 'Glass Supplier'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The name of a supplier from which a piece of glass was procured',
    bounds=CategoricalBounds(['McMaster Carr']),
    )

name = 'Glass Part Number'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description="The manufacturer's part number for a piece of glass that was purchased",
    bounds=CategoricalBounds(['B8476012']),
    )

name = 'Processing Route'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Possible values in the "Processing Route" dropdown menu in the "Sample" layout',
    bounds=CategoricalBounds(['4Bc']),
    )

# Conditions

name = 'Composition Measure'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Possible values of the "Percentage Measure" radial button in the "Sample" layout',
    bounds=CategoricalBounds(['Atomic Percent','Weight Percent'])
    )

name = 'Processing Geometry'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Possible values in the "Processing Geometry" menu buttons in the "Sample" layout',
    bounds=CategoricalBounds(['Billet','Plate'])
    )

name = 'Processing Temperature'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Temperature at which a raw material is processed to produce a Laser Shock Sample',
    bounds=RealBounds(0,1e3,'C')
    )
