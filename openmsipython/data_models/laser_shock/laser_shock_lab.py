#imports
import os, pathlib, methodtools, json, requests, getpass, fmrest
from gemd.util.impl import recursive_foreach
from gemd.entity.util import complete_material_history
from gemd.json import GEMDJson
from ...data_file_io.data_file_directory import DataFileDirectory
from ..utilities import cached_isinstance_generator, get_tag_value_from_list, get_json_filename_for_gemd_object
from ..cached_isinstance_functions import isinstance_spec, isinstance_run, isinstance_process_spec
from ..cached_isinstance_functions import isinstance_ingredient_spec, isinstance_material_ingredient_spec
from ..gemd_template_store import GEMDTemplateStore
from ..gemd_spec_store import GEMDSpecStore
from ..spec_from_filemaker_record import SpecFromFileMakerRecord
from ..run_from_filemaker_record import MaterialRunFromFileMakerRecord, RunFromFileMakerRecord
from .config import LASER_SHOCK_CONST
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .glass_ID import LaserShockGlassID
from .epoxy_ID import LaserShockEpoxyID
from .foil_ID import LaserShockFoilID
from .spacer_ID import LaserShockSpacerID
from .flyer_cutting_program import LaserShockFlyerCuttingProgram
from .spacer_cutting_program import LaserShockSpacerCuttingProgram
from .flyer_stack import LaserShockFlyerStack
from .sample import LaserShockSample
from .launch_package import LaserShockLaunchPackage
from .experiment import LaserShockExperiment

#Some cached isinstance functions to reduce overhead
isinstance_spec_from_filemaker_record = cached_isinstance_generator(SpecFromFileMakerRecord)
isinstance_run_from_filemaker_record = cached_isinstance_generator(RunFromFileMakerRecord)
isinstance_material_run_from_filemaker_record = cached_isinstance_generator(MaterialRunFromFileMakerRecord)

class LaserShockLab(DataFileDirectory) :
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
    
    @methodtools.lru_cache()
    @property
    def all_top_objs(self) :
        all_top_objs = []
        for obj_list in self.all_object_lists :
            for obj in obj_list :
                all_top_objs.append(obj.gemd_object)
        return all_top_objs

    @methodtools.lru_cache()
    @property
    def specs_from_records(self) :
        specs_from_records = []
        for obj_list in self.all_object_lists :
            for obj in obj_list :
                if isinstance_spec_from_filemaker_record(obj) :
                    specs_from_records.append(obj)
        return specs_from_records

    @methodtools.lru_cache()
    @property
    def runs_from_records(self) :
        runs_from_records = []
        for obj_list in self.all_object_lists :
            for obj in obj_list :
                if isinstance_run_from_filemaker_record(obj) :
                    runs_from_records.append(obj)
        return runs_from_records

    #################### PUBLIC METHODS ####################

    def __init__(self,dirpath=pathlib.Path('./gemd_data_model_dumps'),*args,**kwargs) :
        """
        dirpath = path to the directory that should hold the log file and any other output (like the JSON dumps)
        """
        #define the output location
        if not dirpath.is_dir() :
            dirpath.mkdir(parents=True)
        #start up the logger
        if kwargs.get('logger_file') is None :
            kwargs['logger_file'] = dirpath
        super().__init__(dirpath,*args,**kwargs)
        #initialize empty username/password
        self.__username = None; self.__password = None
        #JSON encoder
        self.encoder = GEMDJson()
        #build the template store from what's in the directory already, plus what's hard coded
        try :
            self._template_store = GEMDTemplateStore(self.dirpath,ATTR_TEMPL,OBJ_TEMPL,self.encoder)
        except Exception as e :
            self.logger.error('ERROR: failed to instantiate the template store! Will reraise exception.',exc_obj=e)
        msg = f'Template store initialized with {self._template_store.n_hardcoded} hardcoded templates and '
        msg+= f'{self._template_store.n_from_files} templates read from files in {self.dirpath}'
        self.logger.info(msg)
        #build the spec store from what's in the directory
        try :
            self._spec_store = GEMDSpecStore(self.dirpath,self.encoder)
        except Exception as e :
            self.logger.error(f'ERROR: failed to instantiate the spec store! Will reraise exception.',exc_obj=e)
        msg=f'Spec store initialized with {self._spec_store.n_specs} specs read from files in {self.dirpath}'
        #register the UIDs in the template and spec stores as already written
        self.__uids_written = []
        for template in self._template_store.all_templates :
            self.__uids_written.append(template.uids[self.encoder.scope])
        for spec in self._spec_store.all_specs :
            self.__uids_written.append(spec.uids[self.encoder.scope])
        self.logger.info(msg)

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
        self.logger.info(msg)
        #add all the information to the lab object based on entries in the FileMaker DB
        #"Inventory" pages (create Specs)
        self.logger.debug('Creating Inventory objects...')
        self.glass_IDs = self.get_objects_from_records(LaserShockGlassID,'Glass ID',**extra_kwargs)
        self.logger.debug(f'Created {len(self.glass_IDs)} new Glass ID objects')
        self.foil_IDs = self.get_objects_from_records(LaserShockFoilID,'Foil ID',**extra_kwargs)
        self.logger.debug(f'Created {len(self.foil_IDs)} new Foil ID objects')
        self.epoxy_IDs = self.get_objects_from_records(LaserShockEpoxyID,'Epoxy ID',**extra_kwargs)
        self.logger.debug(f'Created {len(self.epoxy_IDs)} new Epoxy ID objects')
        self.spacer_IDs = self.get_objects_from_records(LaserShockSpacerID,'Spacer ID',**extra_kwargs)
        self.logger.debug(f'Created {len(self.spacer_IDs)} new Spacer ID objects')
        self.flyer_cutting_programs = self.get_objects_from_records(LaserShockFlyerCuttingProgram,
                                                                    'Flyer Cutting Program',**extra_kwargs)
        self.logger.debug(f'Created {len(self.flyer_cutting_programs)} new Flyer Cutting Program objects')
        self.spacer_cutting_programs = self.get_objects_from_records(LaserShockSpacerCuttingProgram,
                                                                     'Spacer Cutting Program',**extra_kwargs)
        self.logger.debug(f'Created {len(self.spacer_cutting_programs)} new Spacer Cutting Program objects')
        #Flyer Stacks (Materials)
        self.logger.debug('Creating Flyer Stacks...')
        self.flyer_stacks = self.get_objects_from_records(LaserShockFlyerStack,'Flyer Stack',self.glass_IDs,
                                                          self.foil_IDs,self.epoxy_IDs,self.flyer_cutting_programs,
                                                          **extra_kwargs)
        self.logger.debug(f'Created {len(self.flyer_stacks)} new Flyer Stack objects')
        #Samples (Materials)
        self.logger.debug('Creating Samples...')
        self.samples = self.get_objects_from_records(LaserShockSample,'Sample',**extra_kwargs)
        self.logger.debug(f'Created {len(self.samples)} new Sample objects')
        #Launch packages (Materials)
        self.logger.debug('Creating Launch Packages...')
        self.launch_packages = self.get_objects_from_records(LaserShockLaunchPackage,'Launch Package',self.flyer_stacks,
                                                             self.spacer_IDs,self.spacer_cutting_programs,self.samples,
                                                             **extra_kwargs)
        self.logger.debug(f'Created {len(self.launch_packages)} new Launch Package objects')
        #Experiments (Measurements)
        self.logger.debug('Creating Experiments...')
        self.experiments = self.get_objects_from_records(LaserShockExperiment,'Experiment',self.launch_packages,
                                                         **extra_kwargs)
        self.logger.debug(f'Created {len(self.experiments)} new Experiment objects')
        self.logger.debug(f'{self._spec_store.n_specs} total unique Specs stored')
        self.logger.info('Done creating GEMD objects')
    
    def get_objects_from_records(self,obj_type,layout_name,*args,n_max_records=100000,records_dict=None,**kwargs) :
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
            all_records = records_dict[layout_name]
        else :
            #get records from the FileMaker server
            all_records = self.__get_filemaker_records(layout_name,n_max_records)
        #get recordId/modId pairs for all existing objects of this type that are in the directory already
        existing_rec_mod_ids = {}
        for fp in self.dirpath.glob(f'{obj_type.__name__}_*.json') :
            with open(fp,'r') as ofp :
                as_json = json.load(ofp)
            tags = as_json['tags']
            try :
                rec_id = get_tag_value_from_list(tags,'recordId')
                mod_id = get_tag_value_from_list(tags,'modId')
            except Exception as e :
                errmsg = f'ERROR: failed to find a recordId and modId from json file {fp.name} '
                errmsg+= f'from a FileMaker record! Will reraise exception. JSON contents: {as_json}'
                self.logger.error(errmsg,exc_obj=e)
            existing_rec_mod_ids[rec_id]=mod_id
        #make the list of records that are new or have been modified from what's currently in the json
        n_recs_skipped = 0
        records_to_use = []
        for record in all_records :
            if record['recordId'] in existing_rec_mod_ids.keys() :
                if record['modId']==existing_rec_mod_ids[record['recordId']] :
                    n_recs_skipped+=1
                    continue
            records_to_use.append(record)
        if n_recs_skipped>0 :
            self.logger.info(f'Skipped {n_recs_skipped} {layout_name} records that already exist in {self.dirpath}')
        #create the new objects
        for ir,record in enumerate(records_to_use) :
            if ir>0 and ir%25==0 :
                self.logger.debug(f'\tCreating {obj_type.__name__} {ir} of {len(records_to_use)}...')
            objs.append(obj_type(record,*args,
                                 templates=self._template_store,specs=self._spec_store,logger=self.logger,**kwargs))
        if len(objs)<=0 :
            return objs
        self.__check_unique_values(objs)
        return objs

    def dump_to_json_files(self,n_max_objs=-1,complete_histories=False,indent=None,recursive=True) :
        """
        Write out GEMD object json files
        
        n_max_objs = the maximum number of objects of each type to dump to json files
            (default = -1 writes out all objects)
        complete_histories = if True, complete material histories are written out for any
            MaterialRunFromFileMakerRecord objects (default = False)
        indent = the indent to use when the files are written out (argument to json.dump). 
            Default results in most compact representation
        recursive = if True, also write out json files for all objects linked to each chosen object
        """
        self.logger.info('Dumping GEMD objects to JSON files...')
        #set a variable so the recursive function knows how to dump the files
        self.__indent = indent
        #dump the different "Run" parts of the lab data model to json files
        for obj_list in self.all_object_lists :
            objs_to_dump = obj_list[:min(n_max_objs,len(obj_list))] if n_max_objs>0 else obj_list
            for obj in objs_to_dump :
                obj_to_write = obj.gemd_object
                fn = f'{obj.__class__.__name__}_recordId_{obj.get_tag_value("recordId")}.json'
                with open(self.dirpath/fn,'w') as fp :
                    fp.write(self.encoder.thin_dumps(obj_to_write,indent=indent))
                if complete_histories :
                    if isinstance_material_run_from_filemaker_record(obj) :
                        context_list = complete_material_history(obj_to_write)
                        with open(self.dirpath/fn.replace('.json','_material_history.json'),'w') as fp :
                            fp.write(json.dumps(context_list,indent=indent))
                self.__uids_written.append(obj_to_write.uids["auto"])
                if recursive :
                    recursive_foreach(obj_to_write,self.__dump_run_objs_to_json)
        #dump the specs in the spec store
        for spec in self._spec_store.all_specs :
            self.__dump_obj_to_json(spec)
        #dump the templates in the template store
        for template in self._template_store.all_templates :
            self.__dump_obj_to_json(template)
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

    def __dump_run_objs_to_json(self,item) :
        if not isinstance_run(item) :
            return
        self.__dump_obj_to_json(item)

    def __dump_obj_to_json(self,item) :
        uid = item.uids["auto"]
        if uid not in self.__uids_written :
            fn = get_json_filename_for_gemd_object(item,self.encoder)
            with open(self.dirpath/fn,'w') as fp :
                fp.write(self.encoder.thin_dumps(item,indent=self.__indent))
            self.__uids_written.append(uid)

#################### MAIN FUNCTION ####################

def main() :
    #build the model of the lab
    model = LaserShockLab()
    model.create_gemd_objects()
    #dump its pieces to json files
    model.dump_to_json_files()

if __name__=='__main__' :
    main()
