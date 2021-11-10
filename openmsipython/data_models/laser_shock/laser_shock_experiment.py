#imports
from hashlib import sha512
from gemd.entity.value import DiscreteCategorical, NominalReal
from gemd.entity.attribute import Parameter, Condition
from .utilities import search_for_single_name
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .laser_shock_spec_for_run import LaserShockSpecForRun
from .run_from_filemaker_record import MeasurementRunFromFileMakerRecord

class LaserShockExperimentSpec(LaserShockSpecForRun) :
    """
    Dynamically-created Spec for a LaserShockExperiment (MeasurementSpec)
    """

    def __init__(self,*args,**kwargs) :
        self.kwargs = kwargs
        super().__init__(*args,**kwargs)

    def get_arg_hash(self) :
        """
        Placeholder for now; I won't be using this in the very near future
        """
        arg_hash = sha512()
        arg_hash.update(self.kwargs.get('exp_type').encode())
        return arg_hash.hexdigest()

    def get_spec_kwargs(self) :
        spec_kwargs = {}
        #name
        exp_type = self.kwargs.get('exp_type')
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
        conditions.append(Condition(name='Fluence',
                                    value=NominalReal(self.kwargs.get('fluence'),
                                                      ATTR_TEMPL['Fluence'].bounds.default_units),
                                    template=ATTR_TEMPL['Fluence'],
                                    origin='calculated'))
        names = [
            'Beam Shaper Input Beam Diameter',
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
        ]
        namesvals = [(name,self.kwargs.get(name)) for name in names]
        for name,val in namesvals :
            if val in ('','N/A','?') :
                continue
            temp = ATTR_TEMPL[name]
            conditions.append(Condition(name=name.replace(' ',''),
                                        value=DiscreteCategorical({val:1.0}),
                                        template=temp,
                                        origin='specified'))
        names = [
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
            conditions.append(Condition(name=name.replace(' ',''),
                                        value=NominalReal(val,temp.bounds.default_units),
                                        template=temp,
                                        origin='specified'))
        return conditions

    def __get_parameters(self) :
        """
        Helper function to return the conditions for this measurement spec
        """
        parameters = []
        names = [
            'Effective Focal Length',
            'Drive Laser Mode',
            'Oscillator Setting',
            'Amplifier Setting',
            'Focusing Lens Arrangement',
            'System Configuration',
            'Speed',
            'Exposure',
        ]
        namesvals = [(name,self.kwargs.get(name)) for name in names]
        for name,val in namesvals :
            if val=='' :
                continue
            temp = ATTR_TEMPL[name]
            parameters.append(Parameter(name=name.replace(' ',''),
                                        value=DiscreteCategorical({val:1.0}),
                                        template=temp,
                                        origin='specified'))
        names = [
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
            parameters.append(Parameter(name=name.replace(' ',''),
                                        value=NominalReal(val,temp.bounds.default_units),
                                        template=temp,
                                        origin='specified'))
        return parameters

class LaserShockExperiment(MeasurementRunFromFileMakerRecord) :
    
    performed_by_key='Performed By'
    performed_date_key='Date'
    notes_key='Notes & Comments'
    ignored = ['Check Energy','Check Alignment','Check Beam Path','Check Camera','Check Illumination','Check Main Amp',
               'Check PDV','Check PreAmp','Check Triggers','Check Launch ID','Check Recover Sample',
               'Check Previous Sample','Check Protection','Check Protection Again','Check Beam Profiler',
               'Check Save','Check Safety']

    def __init__(self,record,specs,launch_packages) :
        #find the launch package that was used
        self.launch_package = search_for_single_name(launch_packages,record.pop('Launch ID'))
        #init the MeasurementRun
        super().__init__(record,self.launch_package,specs)

    @property
    def tags_keys(self) :
        """
        Add the location of the recovered sample, and some other information
        """
        return [*super().tags_keys,
                'Recovery Box','Recovery Row','Recovery Column',
                'New Energy Measurement',
                'Grant Funding'
            ]

    @property
    def file_links_dicts(self) :
        """
        Adding any linked filenames with the filename in "filename" and the "url" 
        explaining what the file is since FileLinks don't have notes : /
        """
        return [
            {'filename':'Camera Filename','url':'Camera'},
            {'filename':'Scope Filename','url':'Scope'},
            {'filename':'Beam Profile Filename','url':'Beam Profiler'},
            ]

    @property
    def measured_property_dict(self):
        d = {}
        names = ['Flyer Tilt','Flyer Curvature','Launch Package Orientation','Video Quality','Spall State']
        for name in names :
            d[name] = {'valuetype':DiscreteCategorical,'template':ATTR_TEMPL[name]}
        names = ['Return Signal Strength','Max Velocity','Est Impact Velocity']
        for name in names :
            d[name] = {'valuetype':NominalReal,'template':ATTR_TEMPL[name]}
        return d

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
            'PDV spot flyer ratio', #'?' is possible
            'Sample Recovery Method',
            'Launch Ratio', #'?' is possible
            'Launch Package Holder',
        ]
        for name in names :
            kwargs[name] = record.pop(name)
        return kwargs
