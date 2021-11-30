#imports
import os, pathlib, json, requests, getpass, fmrest
from gemd.json import GEMDJson
from gemd.entity.util import complete_material_history
from ...utilities.logging import LogOwner
from .laser_shock_glass_ID import LaserShockGlassID
from .laser_shock_epoxy_ID import LaserShockEpoxyID
from .laser_shock_foil_ID import LaserShockFoilID
from .laser_shock_spacer_ID import LaserShockSpacerID
from .laser_shock_flyer_cutting_program import LaserShockFlyerCuttingProgram
from .laser_shock_spacer_cutting_program import LaserShockSpacerCuttingProgram
from .laser_shock_flyer_stack import LaserShockFlyerStack
from .laser_shock_sample import LaserShockSample
from .laser_shock_launch_package import LaserShockLaunchPackage
from .laser_shock_experiment import LaserShockExperiment

class LaserShockLab(LogOwner) :
    """
    Representation of all the information in the Laser Shock Lab's FileMaker database in GEMD language
    """

    #################### CONSTANTS AND PROPERTIES ####################

    FILEMAKER_SERVER_IP_ADDRESS = 'https://10.173.38.223'
    DATABASE_NAME = 'Laser Shock'

    #################### PUBLIC METHODS ####################

    def __init__(self,*args,**kwargs) :
        #define the output location
        self.ofd = pathlib.Path('./gemd_data_model_dumps')
        if not self.ofd.is_dir() :
            self.ofd.mkdir(parents=True)
        #start up the logger
        if kwargs.get('logger_file') is None :
            kwargs['logger_file'] = self.ofd
        super().__init__(*args,**kwargs)
        #get login credentials from the user
        self.username = os.path.expandvars('$JHED_UNAME')
        if self.username=='$JHED_UNAME' :
            self.username = (input('Please enter your JHED username: ')).rstrip()
        self.password = os.path.expandvars('$JHED_PWORD')
        if self.password=='$JHED_PWORD' :
            self.password = getpass.getpass(f'Please enter the JHED password for {self.username}: ')
        #add all the information to the lab object based on entries in the FileMaker DB
        self.logger.info('Creating GEMD objects from FileMakerDB entries')
        #"Inventory" pages (create Specs)
        self.logger.debug('Creating Inventory objects...')
        self.glass_IDs = self.__get_glass_IDs()
        self.epoxy_IDs = self.__get_epoxy_IDs()
        self.foil_IDs = self.__get_foil_IDs()
        self.spacer_IDs = self.__get_spacer_IDs()
        self.flyer_cutting_programs = self.__get_flyer_cutting_programs()
        self.spacer_cutting_programs = self.__get_spacer_cutting_programs()
        #Flyer Stacks (Materials)
        self.logger.debug('Creating Flyer Stacks...')
        self.flyer_stacks = self.__get_flyer_stacks()
        #Samples (Materials)
        self.logger.debug('Creating Samples...')
        self.samples = self.__get_samples()
        #Launch packages (Materials)
        self.logger.debug('Creating Launch Packages...')
        self.launch_packages = self.__get_launch_packages()
        #Experiments (Measurements)
        self.logger.debug('Creating Experiments...')
        self.experiments = self.__get_experiments()
        #Make sure that there is only one of each unique spec (dynamically-created specs may be duplicated)
        self.logger.debug('Replacing duplicated Specs...')
        self.__replace_specs()
        self.logger.info('Done creating GEMD objects')

    def dump_to_json_files(self) :
        """
        Write out different parts of the lab as json files
        """
        self.logger.info('Dumping GEMD objects to JSON files...')
        #create the encoder
        encoder = GEMDJson()
        #dump the different parts of the lab data model to json files
        with open(self.ofd/'glass_ID.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.glass_IDs[0].spec, indent=2))
        with open(self.ofd/'glass_ID_process.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.glass_IDs[0].spec.process, indent=2))
        with open(self.ofd/'epoxy_ID.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.epoxy_IDs[0].spec, indent=2))
        with open(self.ofd/'foil_ID.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.foil_IDs[0].spec, indent=2))
        with open(self.ofd/'spacer_ID.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.spacer_IDs[0].spec, indent=2))
        with open(self.ofd/'flyer_cutting_program.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.flyer_cutting_programs[0].spec, indent=2))
        with open(self.ofd/'spacer_cutting_program.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.spacer_cutting_programs[0].spec, indent=2))
        with open(self.ofd/'flyer_stack.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.flyer_stacks[39].run, indent=2))
        with open(self.ofd/'flyer_stack_spec.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.flyer_stacks[39].run.spec, indent=2))
        with open(self.ofd/'flyer_stack_material_history.json', 'w') as fp: 
            context_list = complete_material_history(self.flyer_stacks[39].run) 
            fp.write(json.dumps(context_list, indent=2))
        with open(self.ofd/'sample_spec.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.samples[0].run.spec, indent=2))
        with open(self.ofd/'sample.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.samples[0].run, indent=2))
        with open(self.ofd/'sample_material_history.json', 'w') as fp :
            context_list = complete_material_history(self.samples[0].run) 
            fp.write(json.dumps(context_list, indent=2))
        with open(self.ofd/'launch_package.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.launch_packages[10].run, indent=2))
        with open(self.ofd/'launch_package_spec.json', 'w') as fp: 
            fp.write(encoder.thin_dumps(self.launch_packages[10].run.spec, indent=2))
        with open(self.ofd/'launch_package_material_history.json', 'w') as fp: 
            context_list = complete_material_history(self.launch_packages[10].run) 
            fp.write(json.dumps(context_list, indent=2))
        with open(self.ofd/'experiment_template.json','w') as fp :
            fp.write(encoder.thin_dumps(self.experiments[0].run.template, indent=2))
        with open(self.ofd/'experiment_spec.json','w') as fp :
            fp.write(encoder.thin_dumps(self.experiments[0].run.spec, indent=2))
        with open(self.ofd/'experiment.json','w') as fp :
            fp.write(encoder.thin_dumps(self.experiments[0].run, indent=2))
        self.logger.info('Done.')

    #################### PRIVATE HELPER FUNCTIONS ####################

    def __get_filemaker_records(self,layout_name,n_max_records=1000) :
        #disable warnings
        requests.packages.urllib3.disable_warnings()
        #create the server
        fms = fmrest.Server(self.FILEMAKER_SERVER_IP_ADDRESS,
                            user=self.username,
                            password=self.password,
                            database=self.DATABASE_NAME,
                            layout=layout_name,
                            verify_ssl=False,
                           )
        #login
        fms.login()
        #return records in the foundset
        return fms.get_records(limit=n_max_records)

    def __get_glass_IDs(self) :
        glassIDs = []
        #get records from the FileMaker server
        records = self.__get_filemaker_records('Glass ID')
        for record in records :
            glassIDs.append(LaserShockGlassID(record,logger=self.logger))
        return glassIDs

    def __get_epoxy_IDs(self) :
        epoxyIDs = []
        records = self.__get_filemaker_records('Epoxy ID')
        for record in records :
            epoxyIDs.append(LaserShockEpoxyID(record,logger=self.logger))
        return epoxyIDs

    def __get_foil_IDs(self) :
        foilIDs = []
        records = self.__get_filemaker_records('Foil ID')
        for record in records :
            foilIDs.append(LaserShockFoilID(record,logger=self.logger))
        return foilIDs

    def __get_spacer_IDs(self) :
        spacerIDs = []
        records = self.__get_filemaker_records('Spacer ID')
        for record in records :
            spacerIDs.append(LaserShockSpacerID(record,logger=self.logger))
        return spacerIDs

    def __get_flyer_cutting_programs(self) :
        flyercuttingprograms = []
        records = self.__get_filemaker_records('Flyer Cutting Program')
        for record in records :
            flyercuttingprograms.append(LaserShockFlyerCuttingProgram(record,logger=self.logger))
        return flyercuttingprograms

    def __get_spacer_cutting_programs(self) :
        spacercuttingprograms = []
        records = self.__get_filemaker_records('Spacer Cutting Program')
        for record in records :
            spacercuttingprograms.append(LaserShockSpacerCuttingProgram(record,logger=self.logger))
        return spacercuttingprograms

    def __get_flyer_stacks(self) :
        flyerstacks = []
        records = self.__get_filemaker_records('Flyer Stack')
        for record in records :
            flyerstacks.append(LaserShockFlyerStack(record,self.glass_IDs,self.foil_IDs,self.epoxy_IDs,
                                                    self.flyer_cutting_programs,logger=self.logger))
        return flyerstacks

    def __get_samples(self) :
        samples = []
        records = self.__get_filemaker_records('Sample')
        for record in records :
            samples.append(LaserShockSample(record,logger=self.logger))
        return samples

    def __get_launch_packages(self) :
        launchpackages = []
        records = self.__get_filemaker_records('Launch Package')
        for record in records :
            launchpackages.append(LaserShockLaunchPackage(record,self.flyer_stacks,self.spacer_IDs,
                                                          self.spacer_cutting_programs,self.samples,logger=self.logger))
        return launchpackages

    def __get_experiments(self) :
        experiments = []
        records = self.__get_filemaker_records('Experiment')
        for record in records :
            experiments.append(LaserShockExperiment(record,self.launch_packages,logger=self.logger))
        return experiments

    def __replace_specs(self) :
        #print(self.samples[0])
        pass

#################### MAIN FUNCTION ####################

def main() :
    #build the model of the lab
    model = LaserShockLab()
    #dump its pieces to json files
    model.dump_to_json_files()

if __name__=='__main__' :
    main()
