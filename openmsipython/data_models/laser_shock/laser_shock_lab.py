#imports
import os, pathlib, json, requests, getpass, fmrest
from gemd.util.impl import recursive_foreach
from gemd.entity.util import complete_material_history
from gemd.json import GEMDJson
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun
from ...utilities.logging import LogOwner
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord, RunFromFileMakerRecord
from .spec_from_filemaker_record import SpecFromFileMakerRecord
from .config import LASER_SHOCK_CONST
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

    #################### PROPERTIES ####################

    @property
    def username(self) :
        if self.__username is None :
            self.__username = os.path.expandvars('$JHED_UNAME')
            if self.__username=='$JHED_UNAME' :
                self.__username = (input('Please enter your JHED username: ')).rstrip()
        return self.__username

    @property
    def password(self) :
        if self.__password is None :
            self.__password = os.path.expandvars('$JHED_PWORD')
            if self.__password=='$JHED_PWORD' :
                self.__password = getpass.getpass(f'Please enter the JHED password for {self.username}: ')
        return self.__password

    @property
    def all_object_lists(self) :
        return [self.glass_IDs,self.epoxy_IDs,self.foil_IDs,self.spacer_IDs,self.flyer_cutting_programs,
                self.spacer_cutting_programs,self.flyer_stacks,self.samples,self.launch_packages,self.experiments]
    
    @property
    def all_top_objs(self) :
        all_top_objs = []
        for obj_list in self.all_object_lists :
            for obj in obj_list :
                all_top_objs.append(obj.gemd_object)
        return all_top_objs

    @property
    def specs_from_records(self) :
        specs_from_records = []
        for obj_list in self.all_object_lists :
            for obj in obj_list :
                if isinstance(obj,SpecFromFileMakerRecord) :
                    specs_from_records.append(obj)
        return specs_from_records

    #################### PUBLIC METHODS ####################

    def __init__(self,*args,working_dir=pathlib.Path('./gemd_data_model_dumps'),**kwargs) :
        """
        working_dir = path to the directory that should hold the log file and any other output (like the JSON dumps)
        """
        #define the output location
        self.ofd = working_dir
        if not self.ofd.is_dir() :
            self.ofd.mkdir(parents=True)
        #start up the logger
        if kwargs.get('logger_file') is None :
            kwargs['logger_file'] = self.ofd
        super().__init__(*args,**kwargs)
        #initialize empty username/password
        self.__username = None; self.__password = None

    def create_gemd_objects(self,records_dict=None) :
        """
        Create GEMD objects, either from the FileMaker database or from a dictionary of records keyed by layout name
        """
        #set up using either the dictionary of records or the FileMaker DB
        msg = 'Creating GEMD objects from '
        if records_dict is not None :
            msg+='records dictionary'
            extra_kwargs = {'records_dict':records_dict}
        else :
            msg+='FileMakerDB entries'
            extra_kwargs = {}
        #add all the information to the lab object based on entries in the FileMaker DB
        self.logger.info(msg)
        #"Inventory" pages (create Specs)
        self.logger.debug('Creating Inventory objects...')
        self.glass_IDs = self.get_objects(LaserShockGlassID,'Glass ID',**extra_kwargs)
        self.logger.debug(f'Created {len(self.glass_IDs)} Glass ID objects...')
        self.epoxy_IDs = self.get_objects(LaserShockEpoxyID,'Epoxy ID',**extra_kwargs)
        self.logger.debug(f'Created {len(self.epoxy_IDs)} Epoxy ID objects...')
        self.foil_IDs = self.get_objects(LaserShockFoilID,'Foil ID',**extra_kwargs)
        self.logger.debug(f'Created {len(self.foil_IDs)} Foil ID objects...')
        self.spacer_IDs = self.get_objects(LaserShockSpacerID,'Spacer ID',**extra_kwargs)
        self.logger.debug(f'Created {len(self.spacer_IDs)} Spacer ID objects...')
        self.flyer_cutting_programs = self.get_objects(LaserShockFlyerCuttingProgram,'Flyer Cutting Program',
                                                       **extra_kwargs)
        self.logger.debug(f'Created {len(self.flyer_cutting_programs)} Flyer Cutting Program objects...')
        self.spacer_cutting_programs = self.get_objects(LaserShockSpacerCuttingProgram,'Spacer Cutting Program',
                                                        **extra_kwargs)
        self.logger.debug(f'Created {len(self.spacer_cutting_programs)} Spacer Cutting Program objects...')
        #Flyer Stacks (Materials)
        self.logger.debug('Creating Flyer Stacks...')
        self.flyer_stacks = self.get_objects(LaserShockFlyerStack,'Flyer Stack',self.glass_IDs,self.foil_IDs,
                                             self.epoxy_IDs,self.flyer_cutting_programs,**extra_kwargs)
        self.logger.debug(f'Created {len(self.flyer_stacks)} Flyer Stack objects...')
        #Samples (Materials)
        self.logger.debug('Creating Samples...')
        self.samples = self.get_objects(LaserShockSample,'Sample',**extra_kwargs)
        self.logger.debug(f'Created {len(self.samples)} Sample objects...')
        #Launch packages (Materials)
        self.logger.debug('Creating Launch Packages...')
        self.launch_packages = self.get_objects(LaserShockLaunchPackage,'Launch Package',self.flyer_stacks,
                                                self.spacer_IDs,self.spacer_cutting_programs,self.samples,
                                                **extra_kwargs)
        self.logger.debug(f'Created {len(self.launch_packages)} Launch Package objects...')
        #Experiments (Measurements)
        self.logger.debug('Creating Experiments...')
        self.experiments = self.get_objects(LaserShockExperiment,'Experiment',self.launch_packages,**extra_kwargs)
        self.logger.debug(f'Created {len(self.experiments)} Experiment objects...')
        #Make sure that there is only one of each unique spec (dynamically-created specs may be duplicated)
        self.__replace_specs()
        self.logger.info('Done creating GEMD objects')
    
    def get_objects(self,obj_type,layout_name,*args,n_max_records=1000,records_dict=None,**kwargs) :
        """
        Return a list of LaserShock/GEMD constructs based on FileMaker records 
        or records in a dictionary (useful for testing)

        obj_type = the type of LaserShock/GEMD object that should be created from this set of records
        layout_name = the name of the FileMaker Database layout to get records from
        n_max_records = the maximum number of records to return from FileMaker
        records_dict = an optional dictionary whose keys are layout names and whose values are records 
                       stored as dictionaries; used instead of FileMaker DB information if given 
                       (useful for testing purposes)

        any other args/kwargs get sent to the constructor for obj_type objects
        """
        objs = []
        if records_dict is not None :
            #get records from the dictionary
            records = records_dict[layout_name]
        else :
            #get records from the FileMaker server
            records = self.__get_filemaker_records(layout_name,n_max_records)
        for record in records :
            objs.append(obj_type(record,*args,logger=self.logger,**kwargs))
        if len(objs)<=0 :
            return objs
        self.__check_unique_values(objs)
        return objs

    def dump_to_json_files(self,n_max_objs=-1,complete_histories=False) :
        """
        Write out different parts of the lab as json files
        
        n_max_objs = the maximum number of objects of each type to dump to json files
                     (default = -1 writes out all objects)
        complete_histories = if True, complete material histories are written out for any
                             MaterialRunFromFileMakerRecord objects (default = False)
        """
        self.logger.info('Dumping GEMD objects to JSON files...')
        #create the encoder
        encoder = GEMDJson()
        #dump the different parts of the lab data model to json files
        for obj_list in self.all_object_lists :
            objs_to_dump = obj_list[:min(n_max_objs,len(obj_list))] if n_max_objs>0 else obj_list
            for iobj,obj in enumerate(objs_to_dump,start=1) :
                if isinstance(obj,RunFromFileMakerRecord) :
                    obj_to_write = obj.run
                elif isinstance(obj,SpecFromFileMakerRecord) :
                    obj_to_write = obj.spec
                fn = f'{obj.__class__.__name__}_{iobj}.json'
                with open(self.ofd/fn,'w') as fp :
                    fp.write(encoder.thin_dumps(obj_to_write,indent=2))
                if complete_histories :
                    if isinstance(obj,MaterialRunFromFileMakerRecord) :
                        context_list = complete_material_history(obj_to_write)
                        with open(self.ofd/fn.replace('.json','_material_history.json'),'w') as fp :
                            fp.write(json.dumps(context_list,indent=2))
        self.logger.info('Done.')

    #################### PRIVATE HELPER FUNCTIONS ####################
    
    def __get_filemaker_records(self,layout_name,n_max_records=1000) :
        #disable warnings
        requests.packages.urllib3.disable_warnings()
        #create the server
        fms = fmrest.Server(LASER_SHOCK_CONST.FILEMAKER_SERVER_IP_ADDRESS,
                            user=self.username,
                            password=self.password,
                            database=LASER_SHOCK_CONST.DATABASE_NAME,
                            layout=layout_name,
                            verify_ssl=False,
                           )
        #login
        fms.login()
        #return records in the foundset
        return fms.get_records(limit=n_max_records)

    def __check_unique_values(self,objects) :
        #log warnings if any of the created objects duplicate values that are assumed to be unique
        unique_vals = {}
        for io,obj in enumerate(objects) :
            for uvn,uv in obj.unique_values.items() :
                if uvn not in unique_vals.keys() :
                    if io==0 :
                        unique_vals[uvn] = []
                    else :
                        errmsg = f'ERROR: discovered a {obj.__class__.__name__} object with unrecognized unique value '
                        errmsg+= f'name {uvn}! Recognized names are {unique_vals.keys()}'
                        self.logger.error(errmsg,RuntimeError)
                unique_vals[uvn].append(uv)
        for uvn,uvl in unique_vals.items() :
            done = set()
            for uv in uvl :
                if uv in done :
                    continue
                n_objs_with_val=uvl.count(uv)
                if n_objs_with_val!=1 :
                    msg = f'WARNING: {n_objs_with_val} {obj.__class__.__name__} objects found with {uvn} = {uv} but '
                    msg+= f'{uvn} should be unique!'
                    self.logger.warning(msg)
                done.add(uv)

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
        self.logger.debug('Replacing duplicated top level Specs...')
        for sfr in self.specs_from_records :
            thisspecname = sfr.spec.name
            thisspecdict = sfr.spec.as_dict()
            for specdict,spec in self.__unique_specs_by_name[thisspecname] :
                if thisspecdict==specdict :
                    sfr.spec = spec
                    break
        #replace all of the lower-level specs recursively
        self.logger.debug('Recursively replacing all duplicated lower level Specs...')
        recursive_foreach(self.all_top_objs,self.__replace_duplicated_specs_in_runs)

#################### MAIN FUNCTION ####################

def main() :
    #build the model of the lab
    model = LaserShockLab()
    model.create_gemd_objects()
    #dump its pieces to json files
    model.dump_to_json_files(1,True)

if __name__=='__main__' :
    main()
