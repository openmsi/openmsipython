#imports
from gemd.entity.bounds import IntegerBounds, RealBounds, CategoricalBounds, CompositionBounds
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

name = 'Glass Thickness mm'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The thickness of a piece of glass',
    bounds=RealBounds(0,50,'mm')
    )

name = 'Glass Length mm'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The length of a piece of glass',
    bounds=RealBounds(0,300,'mm')
    )

name = 'Glass Width mm'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The width of a piece of glass',
    bounds=RealBounds(0,300,'mm')
    )

name = 'Foil Thickness'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The thickness of a piece of foil',
    bounds=RealBounds(0,500,'um')
    )

name = 'Epoxy Thickness'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The thickness of a layer of epoxy',
    bounds=RealBounds(-10,100,'um')
    )

name = 'Stack Thickness'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The thickness of a glass/epoxy/foil stack at some point',
    bounds=RealBounds(0,100,'mm')
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

name = 'Bulk Modulus'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The bulk modulus of a material',
    bounds=RealBounds(0,1e3,'GPa'),
    )

name = 'Average Grain Size'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The average size of grains in a material',
    bounds=RealBounds(0,1e3,'um')
    )

name = 'Min Grain Size'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The minimum size of grains in a material',
    bounds=RealBounds(0,1e3,'um')
    )

name = 'Max Grain Size'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The maximum size of grains in a material',
    bounds=RealBounds(0,1e3,'um')
    )

name = 'Spacer Diameter'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The diameter of a spacer in a Launch Package',
    bounds=RealBounds(0,10,'mm')
    )

name = 'Sample Diameter'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The diameter of an impact sample in a Launch Package',
    bounds=RealBounds(0,10,'mm')
    )

name = 'Sample Thickness'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The thickness of an impact sample in a Launch Package',
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

name = 'Mixing Time'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='How long a two-part epoxy is mixed for (integer number of minutes)',
    bounds=IntegerBounds(0,30)
    )

name = 'Resting Time'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='How long a two-part epoxy is rested for after mixing (integer number of minutes)',
    bounds=IntegerBounds(0,30)
    )

name = 'Compression Weight'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='How many pounds of force should be used to compress a glass/epoxy/foil stack while the epoxy cures',
    bounds=RealBounds(0,100,'lb')
    )

name = 'Compression Time'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='How long a glass/epoxy/foil stack should be compressed while the epoxy cures',
    bounds=RealBounds(0,168,'hr')
    )

name = 'Cutting Procedure'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The procedure used to cut flyer discs out of a glass/epoxy/foil stack using the femtosecond laser',
    bounds=CategoricalBounds(['50um Al Original v1','50um Al Optimized v1','50um Al Optimized v2 (2021-10-22)']),
    )

name = 'Flyer Spacing'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The distance between adjacent flyer discs in a Flyer Stack',
    bounds=RealBounds(0,100,'mm'),
    )

name = 'Flyer Diameter'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The diameter of each flyer in a Flyer Stack',
    bounds=RealBounds(0,100,'mm'),
    )

name = 'Rows X Columns'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The number of rows and columns of flyer discs that is cut out of a glass/epoxy/foil stack',
    bounds=IntegerBounds(0,20),
    )

name = 'Processing Route'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Possible values in the "Processing Route" dropdown menu in the "Sample" layout',
    bounds=CategoricalBounds(['4Bc','Solutionized','Aged']),
    )

name = 'Processing Time'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Amount of time a Raw Material is treated to produce a Sample',
    bounds=RealBounds(0,1e3,'hr'),
    )

name = 'Polishing Pad'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='What was used to polish an impact sample intended for a Launch Package',
    bounds=CategoricalBounds(['Diamond','Silicon Carbide']),
    )

name = 'Sample Location'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The location of an impact sample',
    bounds=IntegerBounds(0,100),
    )

name = 'Sample Location Based Order'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The location-based order ID of an impact sample',
    bounds=IntegerBounds(0,100),
    )

name = 'Diamond Grit'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Grit of the diamond pad used to polish an impact sample',
    bounds=CategoricalBounds(['0.10','0.25','0.50','1.0','3.0','9.0','15','30','35','45','60']),
    )

name = 'Silicon Carbide Grit'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Grit of the silicon carbide pad used to polish an impact sample',
    bounds=CategoricalBounds(['2000','1800','1500','1200','1000','800','600','400','320','240','180','120']),
    )

name = 'Flyer Row'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The row that a specific flyer is in within a flyer stack',
    bounds=IntegerBounds(0,20),
    )

name = 'Flyer Column'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The column that a specific flyer is in within a flyer stack',
    bounds=IntegerBounds(0,20),
    )

name = 'Spacer Adhesive'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The adhesive used to attach a spacer to a flyer in a Launch Package',
    bounds=CategoricalBounds(['Loctite 460','Kapton Included Adhesive']),
    )

name = 'Sample Orientation'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The orientation of the impact sample in a Launch Package',
    bounds=CategoricalBounds(['Extrusion Direction','Longitudinal Direction',
                              'Transverse Direction','Normal Direction']),
    )

name = 'Sample Attachment Adhesive'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The adhesive used to attach an impact sample to a flyer/spacer in a Launch Package',
    bounds=CategoricalBounds(['Loctite 460','Kapton Included Adhesive']),
    )

# Conditions

name = 'Compression Method'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Method used to compress a glass/epoxy/flyer stack',
    bounds=CategoricalBounds(['Handclamp','Apparatus'])
    )

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
    bounds=CategoricalBounds(['Billet','Plate','Foil'])
    )

name = 'Processing Temperature'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Temperature at which a raw material is processed to produce a Laser Shock Sample',
    bounds=RealBounds(0,1e3,'degC')
    )

name = 'Impact Sample Cutting Procedure'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='How an impact sample was cut from its larger piece of material',
    bounds=CategoricalBounds(['EDM','Diamond Wire Saw','TEM Punch'])
    )

name = 'Polishing Process'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Process used to polish an impact sample intended for a Launch Package',
    bounds=CategoricalBounds(['Individual','Large Area Plate'])
    )

name = 'Spacer Attachment Method'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Method used to attach a spacer to a flyer in a Launch Package',
    bounds=CategoricalBounds(['Manual','Alignment Stage'])
    )

name = 'Sample Attachment Method'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Method used to attach a sample to a flyer/spacer in a Launch Package',
    bounds=CategoricalBounds(['Manual','Alignment Stage'])
    )
