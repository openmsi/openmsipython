#imports
from gemd.entity.object.measurement_spec import MeasurementSpec
from .laser_shock_experiment_templates import LaserShockExperimentTemplate

class LaserShockExperimentSpec(MeasurementSpec) :
    """
    A GEMD MeasurementSpec for an experiment performed in the Laser Shock lab
    """

    def __init__(self) :
        #define the arguments to the MeasurementSpec
        name = 'Laser Shock Experiment'
        notes = ''
        conditions = [

        ]
        parameters = [

        ]
        template = LaserShockExperimentTemplate
