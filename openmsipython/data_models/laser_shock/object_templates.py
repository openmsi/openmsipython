#imports
from gemd.entity.template import MaterialTemplate, ProcessTemplate, MeasurementTemplate
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

name = 'Epoxy ID'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='An epoxy used in the Laser Shock Lab',
)

name = 'Foil ID'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A foil used in the Laser Shock Lab',
    properties = [ATTR_TEMPL['Foil Thickness'],
                  ATTR_TEMPL['Foil Length'],
                  ATTR_TEMPL['Foil Width'],
                  ATTR_TEMPL['Foil Hardness'],
                  ATTR_TEMPL['Foil Material'],
        ],
)

name = 'Spacer ID'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A spacer used in the Laser Shock Lab',
    properties = [ATTR_TEMPL['Spacer Thickness'],
                  ATTR_TEMPL['Spacer Material'],
                  ATTR_TEMPL['Spacer Adhesive Sides'],
                  ATTR_TEMPL['Adhesive Type'],
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
    properties = [ATTR_TEMPL['Stack Thickness']],
)

name = 'Raw Sample Material'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A raw material that is processed to produced a Laser Shock Sample',
    properties=[ATTR_TEMPL['Sample Material Type'],
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

name = 'Impact Sample'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A piece of a Sample that has been cut and polished to be used as part of a Launch Package',
    properties=[ATTR_TEMPL['Sample Diameter'],
                ATTR_TEMPL['Sample Thickness']
        ],
)

name = 'Launch Package'
OBJ_TEMPL[name] = MaterialTemplate(
    name=name,
    description='A specific flyer in a flyer stack, possibly with a spacer and/or impact sample attached',
)

# Measurements

name = 'Laser Shock Experiment'
OBJ_TEMPL[name] = MeasurementTemplate(
    name=name,
    description='One of several different categories of measurements performed in the Laser Shock lab',
    conditions=[ATTR_TEMPL['Fluence'],
                ATTR_TEMPL['Beam Shaper Input Beam Diameter'],
                ATTR_TEMPL['Beam Shaper'],
                ATTR_TEMPL['Camera Lens'],
                ATTR_TEMPL['Doubler'],
                ATTR_TEMPL['Camera Aperture'],
                ATTR_TEMPL['Lens Aperture'],
                ATTR_TEMPL['Camera Filter'],
                ATTR_TEMPL['Illumination Laser'],
                ATTR_TEMPL['Laser Filter'],
                ATTR_TEMPL['High Speed Camera'],
                ATTR_TEMPL['Beam Profiler Filter'],
                ATTR_TEMPL['Sample Recovery Method'],
                ATTR_TEMPL['Launch Package Holder'],
                ATTR_TEMPL['Energy'],
                ATTR_TEMPL['Theoretical Beam Diameter'],
                ATTR_TEMPL['PreAmp Output Power'],
                ATTR_TEMPL['PDV Spot Size'],
                ATTR_TEMPL['Base Pressure'],
                ATTR_TEMPL['PDV spot flyer ratio'],
                ATTR_TEMPL['Launch Ratio'],
        ],
    parameters=[ATTR_TEMPL['Effective Focal Length'],
                ATTR_TEMPL['Drive Laser Mode'],
                ATTR_TEMPL['Oscillator Setting'],
                ATTR_TEMPL['Amplifier Setting'],
                ATTR_TEMPL['Focusing Lens Arrangement'],
                ATTR_TEMPL['System Configuration'],
                ATTR_TEMPL['Speed'],
                ATTR_TEMPL['Exposure'],
                ATTR_TEMPL['Attenuator Angle'],
                ATTR_TEMPL['Booster Amp Setting'],
                ATTR_TEMPL['Current Set Point'],
                ATTR_TEMPL['Beam Profiler Gain'],
                ATTR_TEMPL['Beam Profiler Exposure'],
        ],
    properties=[ATTR_TEMPL['Flyer Tilt'],
                ATTR_TEMPL['Flyer Curvature'],
                ATTR_TEMPL['Launch Package Orientation'],
                ATTR_TEMPL['Video Quality'],
                ATTR_TEMPL['Spall State'],
                ATTR_TEMPL['Return Signal Strength'],
                ATTR_TEMPL['Max Velocity'],
                ATTR_TEMPL['Est Impact Velocity'],
        ],
)

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

name = 'Purchasing Epoxy'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Purchasing an Epoxy from a manufacturer',
    parameters=[ATTR_TEMPL['Epoxy Supplier'],
        ],
    allowed_names=[],
)

name = 'Purchasing Foil'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Purchasing a foil from a manufacturer',
    parameters=[ATTR_TEMPL['Foil Supplier'],
                ATTR_TEMPL['Foil Part Number'],
        ],
    allowed_names=[],
)

name = 'Purchasing Spacer'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Purchasing a spacer from a manufacturer',
    parameters=[ATTR_TEMPL['Spacer Supplier'],
                ATTR_TEMPL['Spacer Part Number'],
        ],
    allowed_names=[],
)

name = 'Flyer Cutting Program'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='A program (process) for cutting flyers out of a layer of foil',
    conditions=[ATTR_TEMPL['Cutting Method'],
                ATTR_TEMPL['Typical Cutting Time'],
                ATTR_TEMPL['Cutting Tool'],
        ],
    parameters=[ATTR_TEMPL['Laser Cutting Energy'],
                ATTR_TEMPL['Number of Passes'],
                ATTR_TEMPL['Aperture Setting'],
                ATTR_TEMPL['Depth of Cut'],
        ],
)

name = 'Spacer Cutting Program'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='A program (process) for cutting spacers out of a spacer material',
    conditions=[ATTR_TEMPL['Cutting Method'],
                ATTR_TEMPL['Typical Cutting Time'],
        ],
    parameters=[ATTR_TEMPL['Laser Cutting Energy'],
                ATTR_TEMPL['Number of Passes'],
                ATTR_TEMPL['Aperture Setting'],
                ATTR_TEMPL['Depth of Cut'],
        ],
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

name = 'Sample Preprocessing'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Preprocessing a raw material',
    conditions=[ATTR_TEMPL['Preprocessing']],
    parameters=[ATTR_TEMPL['Preprocessing Temperature']],
)

name = 'Sample Processing'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='''Processing a raw material of some type in some geometry, at some temperature,
                   and through some route to produce a Sample for the Laser Shock Lab''',
    conditions=[ATTR_TEMPL['Processing Geometry'],
                ATTR_TEMPL['Material Processing'],
                ATTR_TEMPL['Processing Temperature'],
        ],
    parameters=[
                ATTR_TEMPL['Processing Route'],
                ATTR_TEMPL['Processing Time'],
        ],
)

name = 'Sample Annealing'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Annealing a processed material',
    conditions=[ATTR_TEMPL['Annealing Temperature']],
    parameters=[ATTR_TEMPL['Annealing Time']],
)

name = 'Impact Sample Cutting and Polishing'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Cutting and polishing an impact sample for a Launch Package',
    conditions=[ATTR_TEMPL['Impact Sample Cutting Procedure'],
                ATTR_TEMPL['Polishing Process']
        ],
    parameters=[ATTR_TEMPL['Polishing Pad'],
                ATTR_TEMPL['Diamond Grit'],
                ATTR_TEMPL['Silicon Carbide Grit'],
                ATTR_TEMPL['Sample Location'],
                ATTR_TEMPL['Sample Location Based Order'],
        ],
)

name = 'Choosing Flyer'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Choosing a particular flyer (row, column) from a flyer stack',
    parameters=[
                ATTR_TEMPL['Flyer Row'],
                ATTR_TEMPL['Flyer Column'],
        ],
)

name = 'Cutting Spacer'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Cutting a spacer out of a larger piece of spacer material',
)

name = 'Attaching Spacer'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Attaching a cut out spacer to a specific flyer in a flyer stack',
    conditions=[ATTR_TEMPL['Spacer Attachment Method']],
    parameters=[ATTR_TEMPL['Spacer Adhesive']],
)

name = 'Attaching Sample'
OBJ_TEMPL[name] = ProcessTemplate(
    name=name,
    description='Attaching an impact sample to a specific flyer/spacer for a Launch Package',
    conditions=[ATTR_TEMPL['Sample Attachment Method']],
    parameters=[ATTR_TEMPL['Sample Orientation'],
                ATTR_TEMPL['Sample Attachment Adhesive'],
        ],
)
