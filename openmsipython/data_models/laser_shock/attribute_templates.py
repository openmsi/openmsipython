#imports
import inspect
from gemd.entity.bounds import IntegerBounds, RealBounds, CategoricalBounds, CompositionBounds
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate

ATTR_TEMPL = {}

#################### PROPERTIES ####################

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

name = 'Foil Length'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The length of the Foil',
    bounds=RealBounds(0,50,'in')
)

name = 'Foil Width'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The width of the Foil',
    bounds=RealBounds(0,50,'in')
)

name = 'Foil Hardness'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The type of Hardness of the Foil',
    bounds=CategoricalBounds(['Hard','Soft','Unknown'])
)

name = 'Foil Material'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The type of Material of the Foil',
    bounds=CategoricalBounds(['Aluminum'])
)

name = 'Spacer Thickness'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The thickness of the Spacer',
    bounds=RealBounds(0,500,'um')
)

name = 'Spacer Material'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The material that the Spacer is made of',
    bounds= CategoricalBounds(['Kapton'])
)

name = 'Spacer Adhesive Sides'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The sides of the Spacer Adhesive',
    bounds=CategoricalBounds(['None','Single','Double'])
)

name = 'Adhesive Type'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The type of Adhesive used in the Spacer',
    bounds=CategoricalBounds(['N/A','Silicone','Acrylic'])
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

name = 'Sample Material Type'
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

name = 'Flyer Tilt'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='Amount of tilt observed for a flyer',
    bounds=CategoricalBounds(['None','Minor','Significant'])
)

name = 'Flyer Curvature'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='Amount of curvature observed for a flyer',
    bounds=CategoricalBounds(['None','Minor','Significant'])
)

name = 'Launch Package Orientation'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='Orientation of the launch package',
    bounds=CategoricalBounds(['Flat','Slight Rotation','Major Rotation'])
)

name = 'Video Quality'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='The overall quality of a collected high speed camera video',
    bounds=CategoricalBounds(['Amazing','Great','Good','OK','Eh'])
)

name = 'Spall State'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='Type/amount of spall observed',
    bounds=CategoricalBounds(['No visible','Partial','Full','Through sample'])
)

name = 'Return Signal Strength'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='Power of the laser return signal (units of decibel-milliwatts, dBm, not recognized by GEMD)',
    bounds=RealBounds(0.,1.e3,'')
)

name = 'Max Velocity'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='Maximum velocity measured using PDV',
    bounds=RealBounds(0.,1.e3,'m/s')
)

name = 'Est Impact Velocity'
ATTR_TEMPL[name] = PropertyTemplate(
    name=name,
    description='Estimated velocity of the flyer at impact',
    bounds=RealBounds(0.,1.e3,'m/s')
)

#################### PARAMETERS ####################

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

name = 'Epoxy Supplier'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The name of a supplier from which an Epoxy was procured',
    bounds=CategoricalBounds(['Loctite']),
)

name = 'Foil Supplier'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The name of a supplier from which a foil was procured',
    bounds=CategoricalBounds(['AluFoil']),
)

name = 'Foil Part Number'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description="The manufacturer's part number for a foil that was purchased",
    bounds=CategoricalBounds([]),
)

name = 'Spacer Supplier'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The name of a supplier from which a spacer was procured',
    bounds=CategoricalBounds(['AluFoil']),
)

name = 'Spacer Part Number'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description="The manufacturer's part number for a spacer that was purchased",
    bounds=CategoricalBounds([]),
)

name = 'Laser Cutting Energy'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Energy of the laser used to cut out flyers',
    bounds=RealBounds(0.,500.,'uJ')
)

name = 'Number of Passes'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Number of passes performed in cutting out flyers',
    bounds=IntegerBounds(0,200)
)

name = 'Aperture Setting'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Whether the aperture used during a laser cutting procedure is narrow or open',
    bounds=CategoricalBounds(['Narrow','Open'])
)

name = 'Depth of Cut'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Whether the depth of cut setting is turned on or off during a laser cutting procedure',
    bounds=CategoricalBounds(['On','Off'])
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

name = 'Preprocessing Temperature'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Temperature at which a raw sample is preprocessed',
    bounds=RealBounds(0.,1.e3,'degC'),
)

name = 'Processing Route'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Possible values in the "Processing Route" dropdown menu in the "Sample" layout',
    bounds=CategoricalBounds(['4Bc','1Bc+3Bc','Solutionized','Aged']),
)

name = 'Processing Time'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Amount of time a Raw Material is treated to produce a Sample',
    bounds=RealBounds(0,1e3,'hr'),
)

name = 'Annealing Time'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Amount of time a Raw Material is annealed to produce a Sample',
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

name = 'Effective Focal Length'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The effective focal length of the focusing lens between the beam shaper and power meter',
    bounds=RealBounds(60.,1000.,'mm')
)

name = 'Drive Laser Mode'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Mode in which the drive laser is run',
    bounds=CategoricalBounds(['Long pulse','Q switched'])
)

name = 'Oscillator Setting'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Drive laser oscillator setting',
    bounds=IntegerBounds(0,10)
)

name = 'Amplifier Setting'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Drive laser amplifier setting',
    bounds=IntegerBounds(0,10)
)

name = 'Focusing Lens Arrangement'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Whether the focusing lens in the PDV system is set according to the "new" or "old" arrangement',
    bounds=CategoricalBounds(['Old','New'])
)

name = 'System Configuration'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Whether the PDV system is set up in 1-point or 32-point mode',
    bounds=CategoricalBounds(['1-Point','32-Point'])
)

name = 'Oscilloscope Range'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description="The range setting on the oscilloscope (mV/div, categorical bc it's a dropdown menu)",
    bounds=CategoricalBounds(['50','100','200'])
)

name = 'Speed'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description="The framerate set in the high speed camera software (frames/s, categorical bc it's a dropdown menu)",
    bounds=CategoricalBounds(['60','200','500','1,000','10,000','20,000','50,000','100,000','200,000',
                              '500,000','1,000,000','2,000,000','5,000,000','10,000,000'])
)

name = 'Exposure'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description=inspect.cleandoc("""
        The exposure time set in the high speed camera software (nanoseconds, categorical bc it's a dropdown menu)
        """).replace('\n',''),
    bounds=CategoricalBounds(['100','200','500','1000','10000','20000','50000','100000','200000',
                              '500000','1000000','2000000','5000000','10000000'])
)

name = 'Attenuator Angle'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The angle of the laser attenuator',
    bounds=RealBounds(0,360,'deg')
)

name = 'Booster Amp Setting'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='Setting on the PDV seed signal laser booster amplifier',
    bounds=RealBounds(0.,1.e3,'mV')
)

name = 'Current Set Point'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='',
    bounds=RealBounds(0.,1.,'A_it')
)

name = 'Beam Profiler Gain'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The gain setting on the beam profiler',
    bounds=RealBounds(0.,10.,'dB')
)

name = 'Beam Profiler Exposure'
ATTR_TEMPL[name] = ParameterTemplate(
    name=name,
    description='The exposure time used for the beam profiler',
    bounds=RealBounds(0.,1.e3,'ms')
)

#################### CONDITIONS ####################

name = 'Cutting Method'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Whether something is cut using a laser in pulsed or continuous mode',
    bounds=CategoricalBounds(['Pulsed','Continuous'])
)

name = 'Typical Cutting Time'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='How long it usually takes to cut out some flyers',
    bounds=RealBounds(0.,300.,'min')
)

name = 'Cutting Tool'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The tool used to cut out a set of flyers',
    bounds=CategoricalBounds(['Femtosecond Laser','Laser Cutter'])
)

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

name = 'Preprocessing'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The type of preprocessing performed on a raw material',
    bounds=CategoricalBounds(['ECAE','Rolling'])
)

name = 'Material Processing'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Possible values in the "Processing" check boxes in the "Sample" layout',
    bounds=CategoricalBounds(['ECAE','Rolling'])
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

name = 'Annealing Temperature'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Temperature at which a raw material is annealed to produce a Laser Shock Sample',
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

name = 'Fluence'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The calculated fluence of the laser',
    bounds=RealBounds(0.,100.,'J/cm^2')
)

name = 'Beam Shaper Input Beam Diameter'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The diameter of the laser beam as inputted into the beam shaper',
    bounds=RealBounds(25.,60.,'mm')
)

name = 'Beam Shaper'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The beam shaper used',
    bounds=CategoricalBounds(['Silios','HoloOr'])
)

name = 'Camera Lens'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description="The focal length of the camera used (units are mm, but this is categorical bc it's a dropdown)",
    bounds=CategoricalBounds(['105'])
)

name = 'Doubler'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Setting for the doubler on the high speed camera',
    bounds=CategoricalBounds(['0','1','2'])
)

name = 'Camera Aperture'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The aperture setting on the high speed camera',
    bounds=CategoricalBounds(['0','1','2','3','4','5','6','7'])
)

name = 'Lens Aperture'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The aperture setting on the high speed camera lens',
    bounds=CategoricalBounds(['2.8','4','5.6','8','11','16','22','32'])
)

name = 'Camera Filter'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The filter used on the high speed camera',
    bounds=CategoricalBounds(['648 CWL/20 FWHM','647 CWL/10 FWHM'])
)

name = 'Illumination Laser'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The laser used to illuminate the high speed camera field of view',
    bounds=CategoricalBounds(['SiLux','Cavitar'])
)

name = 'Laser Filter'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The filter applied to the illumination laser',
    bounds=CategoricalBounds(['none','Texwipe/diffuser','IR filter'])
)

name = 'High Speed Camera'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The high speed camera used',
    bounds=CategoricalBounds(['Shimadzu','Kirana','Not Used'])
)

name = 'Beam Profiler Filter'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The filter applied to the beampath sent to the beam profiler',
    bounds=CategoricalBounds(['OD 1','OD 2','OD 3','OD 4','OD 5','OD 6','OD 7','OD 8','OD 9','OD 10'])
)

name = 'Sample Recovery Method'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='How the sample was recovered after impact',
    bounds=CategoricalBounds(['Glass Petri Dish','PDMS','none'])
)

name = 'Launch Package Holder'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The method used to hold the launch package in place',
    bounds=CategoricalBounds(['Simple Clamp','Vacuum Chamber','Kinematic Optical Mount'])
)

name = 'Energy'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The energy of the laser',
    bounds=RealBounds(0.,5.e3,'mJ')
)

name = 'Theoretical Beam Diameter'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The theoretical beam diameter, according to the manufacturer',
    bounds=RealBounds(0.,5.,'mm')
)

name = 'PreAmp Output Power'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description=inspect.cleandoc("""
        The output power of the preamplifier used in the PDV system 
        (units of decibel-milliwatts, dBm, not recognized by GEMD)
        """).replace('\n',''),
    bounds=RealBounds(0.,1.e3,'')
)

name = 'PDV Spot Size'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The diameter of the PDV laser spot',
    bounds=RealBounds(0.,1.e3,'um')
)

name = 'Base Pressure'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='The pressure in the vacuum chamber used to hold the launch package in place',
    bounds=RealBounds(0.,1.e5,'mTorr')
)

name = 'PDV spot flyer ratio'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Ratio of the laser spot diameter to the flyer diameter',
    bounds=RealBounds(0.,10.,'')
)

name = 'Launch Ratio'
ATTR_TEMPL[name] = ConditionTemplate(
    name=name,
    description='Ratio of the PDV spot diameter to the flyer diameter',
    bounds=RealBounds(0.,10.,'')
)
