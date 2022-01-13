#imports
from gemd.entity.value import NominalCategorical, NominalReal, NominalInteger
from gemd.entity.attribute import Parameter, Condition
from gemd.entity.object import MeasurementSpec
from ..utilities import search_for_single_name
from ..spec_for_run import SpecForRun
from ..run_from_filemaker_record import MeasurementRunFromFileMakerRecord
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL

class LaserShockExperimentSpec(SpecForRun) :
    """
    Dynamically-created Spec for a LaserShockExperiment (MeasurementSpec)
    """

    spec_type = MeasurementSpec

    def __init__(self,*args,**kwargs) :
        self.kwargs = kwargs
        super().__init__(*args,**kwargs)

    def get_spec_kwargs(self) :
        spec_kwargs = {}
        #name
        exp_type = self.kwargs.get('Experiment Type')
        spec_kwargs['name'] = exp_type if exp_type!='' else 'Laser Shock Experiment'
        #notes
        spec_kwargs['notes'] = 'A spec for performing a Laser Shock Experiment measurement'
        #conditions
        spec_kwargs['conditions'] = self.__get_conditions()
        #parameters
        spec_kwargs['parameters'] = self.__get_parameters()
        #the template
        spec_kwargs['template'] = OBJ_TEMPL['Laser Shock Experiment']
        return spec_kwargs

    def __get_conditions(self) :
        """
        Helper function to return the conditions for this measurement spec
        """
        conditions = []
        if self.kwargs.get('Fluence')!='' :
            conditions.append(Condition(name='Fluence',
                                        value=NominalReal(self.kwargs.get('Fluence'),
                                                        ATTR_TEMPL['Fluence'].bounds.default_units),
                                        template=ATTR_TEMPL['Fluence'],
                                        origin='computed'))
        names = [
            'Beam Shaper',
            'Camera Lens',
            'Doubler',
            'Camera Aperture',
            'Lens Aperture',
            'Camera Filter',
            'Illumination Laser',
            'Laser Filter',
            'High Speed Camera',
            'Beam Profiler Filter',
            'Sample Recovery Method',
            'Launch Package Holder',
            'Check Vacuum',
        ]
        namesvals = [(name,self.kwargs.get(name)) for name in names]
        for name,val in namesvals :
            if val in ('','N/A','?') :
                continue
            temp = ATTR_TEMPL[name]
            conditions.append(Condition(name=name.replace(' ',''),
                                        value=NominalCategorical(str(val)),
                                        template=temp,
                                        origin='specified'))
        names = [
            'Beam Shaper Input Beam Diameter',
            'Energy',
            'Theoretical Beam Diameter',
            'PreAmp Output Power',
            'PDV Spot Size',
            'Base Pressure',
            'PDV spot flyer ratio',
            'Launch Ratio',
        ]
        namesvals = [(name,self.kwargs.get(name)) for name in names]
        for name,val in namesvals :
            if val in ('','N/A','?') :
                continue
            temp = ATTR_TEMPL[name]
            try :
                conditions.append(Condition(name=name.replace(' ',''),
                                            value=NominalReal(float(val),temp.bounds.default_units),
                                            template=temp,
                                            origin='specified'))
            except ValueError :
                conditions.append(Condition(name=name.replace(' ','')+'CouldNotCast',
                                            value=NominalCategorical(val),
                                            origin='specified'))
        return conditions

    def __get_parameters(self) :
        """
        Helper function to return the conditions for this measurement spec
        """
        parameters = []
        names = [
            'Oscillator Setting',
            'Amplifier Setting',
        ]
        namesvals = [(name,self.kwargs.get(name)) for name in names]
        for name,val in namesvals :
            if val=='' :
                continue
            parameters.append(Parameter(name=name.replace(' ',''),
                                        value=NominalInteger(val),
                                        template=ATTR_TEMPL[name],
                                        origin='specified'))
        names = [
            'Drive Laser Mode',
            'Focusing Lens Arrangement',
            'System Configuration',
            'Oscilloscope Range',
            'Speed',
            'Exposure',
        ]
        namesvals = [(name,self.kwargs.get(name)) for name in names]
        for name,val in namesvals :
            if val in ('','N/A') :
                continue
            temp = ATTR_TEMPL[name]
            parameters.append(Parameter(name=name.replace(' ',''),
                                        value=NominalCategorical(str(val)),
                                        template=temp,
                                        origin='specified'))
        names = [
            'Effective Focal Length',
            'Attenuator Angle',
            'Booster Amp Setting',
            'Current Set Point',
            'Beam Profiler Gain',
            'Beam Profiler Exposure',
        ]
        namesvals = [(name,self.kwargs.get(name)) for name in names]
        for name,val in namesvals :
            if val=='' :
                continue
            temp = ATTR_TEMPL[name]
            try :
                parameters.append(Parameter(name=name.replace(' ',''),
                                            value=NominalReal(float(val),temp.bounds.default_units),
                                            template=temp,
                                            origin='specified'))
            except ValueError :
                parameters.append(Parameter(name=name.replace(' ','')+'CouldNotCast',
                                            value=NominalCategorical(val),
                                            origin='specified'))
        return parameters

class LaserShockExperiment(MeasurementRunFromFileMakerRecord) :
    """
    MeasurementRun representing measurements made using Laser Shock and/or PDV on a particular Launch Package
    """

    spec_type = LaserShockExperimentSpec
    
    performed_by_key='Performed By'
    performed_date_key='Date'
    notes_key='Notes & Comments'
    ignored = ['Check Energy','Check Alignment','Check Beam Path','Check Camera','Check Illumination','Check Main Amp',
               'Check PDV','Check PreAmp','Check Triggers','Check Launch ID','Check Recover Sample',
               'Check Previous Sample','Check Protection','Check Protection Again','Check Beam Profiler',
               'Check Save','Check Safety']

    #################### PROPERTIES ####################

    @property
    def tags_keys(self) :
        """
        Add the location of the recovered sample, and some other information
        """
        return [*super().tags_keys,
                'Recovery Box','Recovery Row','Recovery Column',
                'New Energy Measurement',
                'Grant Funding',
                'Experiment Day Counter'
            ]

    @property
    def file_links_dicts(self) :
        return [
            {'filename':'Camera Filename'},
            {'filename':'Scope Filename'},
            {'filename':'Beam Profile Filename'},
            ]

    @property
    def measured_property_dict(self):
        d = {}
        names = ['Flyer Tilt','Flyer Curvature','Launch Package Orientation',
                 'Video Quality','Spall State','Check Plateau']
        for name in names :
            d[name] = {'valuetype':NominalCategorical,'template':ATTR_TEMPL[name]}
        names = ['Return Signal Strength','Max Velocity','Est Impact Velocity']
        for name in names :
            d[name] = {'valuetype':NominalReal,'datatype':float,'template':ATTR_TEMPL[name]}
        return d

    @property
    def unique_values(self):
        return {**super().unique_values,'Launch ID':self.launch_ID}

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,record,launch_packages,**kwargs) :
        #find the launch package that was used
        logger = kwargs.get('logger')
        self.launch_ID = record.pop('Launch ID')
        self.launch_package = search_for_single_name([lp.run for lp in launch_packages],self.launch_ID,
                                                     logger=logger,raise_exception=(logger is None))
        #init the MeasurementRun
        super().__init__(record,material=self.launch_package,**kwargs)

    def ignore_key(self,key) :
        if key in self.ignored :
            return True
        else :
            return super().ignore_key(key)

    def get_spec_kwargs(self,record) :
        kwargs={}
        names = [
            #the experiment type (used for the name of the spec)
            'Experiment Type',
            #stuff from the laser tab
            #conditions
            'Energy',
            'Theoretical Beam Diameter',
            'Fluence', #calculated
            'Beam Shaper Input Beam Diameter',
            'Beam Shaper',
            #parameters
            'Effective Focal Length',
            'Drive Laser Mode',
            'Oscillator Setting',
            'Amplifier Setting',
            'Attenuator Angle',
            #stuff from the PDV tab
            #conditions
            'PreAmp Output Power',
            'PDV Spot Size',
            #parameters
            'Booster Amp Setting',
            'Focusing Lens Arrangement',
            'System Configuration',
            'Current Set Point',
            'Oscilloscope Range',
            #stuff from the camera tab
            #conditions
            'Camera Lens',
            'Doubler',
            'Camera Aperture',
            'Lens Aperture',
            'Camera Filter',
            'Illumination Laser',
            'Laser Filter',
            'High Speed Camera',
            'Beam Profiler Filter',
            #parameters
            'Speed',
            'Exposure',
            'Beam Profiler Gain',
            'Beam Profiler Exposure',
            #stuff from the launch integration tab
            #conditions
            'Base Pressure',
            'Check Vacuum', # 'On' or 'Off'
            'PDV spot flyer ratio', #'?' is possible
            'Sample Recovery Method',
            'Launch Ratio', #'?' is possible
            'Launch Package Holder',
        ]
        for name in names :
            kwargs[name] = record.pop(name)
        return kwargs
