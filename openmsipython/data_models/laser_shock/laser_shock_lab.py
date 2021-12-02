#imports
import os, pathlib, json, requests, getpass, fmrest
from gemd.util.impl import recursive_foreach
from gemd.entity.util import complete_material_history
from gemd.json import GEMDJson
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun
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

    #################### PROPERTIES ####################

    @property
    def all_top_specs(self) :
        all_top_specs = [gid.spec for gid in self.glass_IDs]
        all_top_specs+= [eid.spec for eid in self.epoxy_IDs]
        all_top_specs+= [fid.spec for fid in self.foil_IDs]
        all_top_specs+= [sid.spec for sid in self.spacer_IDs]
        all_top_specs+= [fcp.spec for fcp in self.flyer_cutting_programs]
        all_top_specs+= [scp.spec for scp in self.spacer_cutting_programs]
        all_top_specs+= [fs.run.spec for fs in self.flyer_stacks]
        all_top_specs+= [s.run.spec for s in self.samples]
        all_top_specs+= [lp.run.spec for lp in self.launch_packages]
        all_top_specs+= [e.run.spec for e in self.experiments]
        return all_top_specs

    @property
    def all_top_objs(self) :
        all_top_objs = [gid.spec for gid in self.glass_IDs]
        all_top_objs+= [eid.spec for eid in self.epoxy_IDs]
        all_top_objs+= [fid.spec for fid in self.foil_IDs]
        all_top_objs+= [sid.spec for sid in self.spacer_IDs]
        all_top_objs+= [fcp.spec for fcp in self.flyer_cutting_programs]
        all_top_objs+= [scp.spec for scp in self.spacer_cutting_programs]
        all_top_objs+= [fs.run for fs in self.flyer_stacks]
        all_top_objs+= [s.run for s in self.samples]
        all_top_objs+= [lp.run for lp in self.launch_packages]
        all_top_objs+= [e.run for e in self.experiments]
        return all_top_objs

    @property
    def specs_from_records(self) :
        specs_from_records = self.glass_IDs+self.epoxy_IDs+self.foil_IDs+self.spacer_IDs
        specs_from_records+= self.flyer_cutting_programs+self.spacer_cutting_programs
        return specs_from_records

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

    def __count_specs(self,item) :
        if not isinstance(item, (MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec)):
            return
        self.__n_total_specs+=1

    def __find_unique_spec_objs(self,item) :
        if not isinstance(item, (MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec)):
            return
        itemname = item.name
        if itemname not in self.__unique_specs_by_name.keys() :
            self.__unique_specs_by_name[itemname] = []
        itemdict = item.as_dict()
        found = False
        for uspecdict,_ in self.__unique_specs_by_name[itemname] :
            if itemdict==uspecdict :
                found = True
                break
        if not found :
            self.__unique_specs_by_name[itemname].append((itemdict,item))

    def __replace_duplicated_specs_in_runs(self,item) :
        #replace specs for MaterialRuns, ProcessRuns, IngredientRuns, and MeasurementRuns
        if isinstance(item,(MaterialRun,ProcessRun,IngredientRun,MeasurementRun)) :
            if item.spec is not None :
                thisspecname = item.spec.name
                thisspecdict = item.spec.as_dict()
                for specdict,spec in self.__unique_specs_by_name[thisspecname] :
                    if thisspecdict==specdict :
                        item.spec = spec
                        break
        return

    def __replace_specs(self) :
        #get a list of all the unique specs that have been dynamically created
        self.logger.debug('Finding the set of unique Specs...')
        self.__n_total_specs = 0
        recursive_foreach(self.all_top_objs,self.__count_specs)
        self.__unique_specs_by_name = {}
        recursive_foreach(self.all_top_objs,self.__find_unique_spec_objs)
        all_unique_specs = []
        for t in self.__unique_specs_by_name.keys() :
            for us in self.__unique_specs_by_name[t] :
                all_unique_specs.append(us)
        self.logger.debug(f'Found {len(all_unique_specs)} unique Specs from a set of {self.__n_total_specs} total')
        #replace duplicate specs in the SpecFromFileMakerRecord objects
        self.logger.debug(f'Replacing duplicated top level Specs...')
        for sfr in self.specs_from_records :
            thisspecname = sfr.spec.name
            thisspecdict = sfr.spec.as_dict()
            for specdict,spec in self.__unique_specs_by_name[thisspecname] :
                if thisspecdict==specdict :
                    sfr.spec = spec
                    break
        #replace all of the lower-level specs recursively
        self.logger.debug(f'Recursively replacing all duplicated lower level Specs...')
        recursive_foreach(self.all_top_objs,self.__replace_duplicated_specs_in_runs)

#################### MAIN FUNCTION ####################

def main() :
    #build the model of the lab
    model = LaserShockLab()
    #dump its pieces to json files
    model.dump_to_json_files()

if __name__=='__main__' :
    main()
