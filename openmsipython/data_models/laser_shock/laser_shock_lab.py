#imports
import os, pathlib, json, requests, getpass, fmrest
from gemd.util.impl import recursive_foreach
from gemd.entity.util import complete_material_history
from gemd.json import GEMDJson
from openmsistream.data_file_io.entity.data_file_directory import DataFileDirectory
from ..utilities import get_tag_value_from_list, get_json_filename_for_gemd_object
from ..cached_isinstance_functions import cached_isinstance_generator
from ..cached_isinstance_functions import isinstance_template, isinstance_spec, isinstance_run, isinstance_material_run
from ..cached_isinstance_functions import isinstance_link_by_uid, isinstance_list_or_tuple, isinstance_dict_serializable
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
COMPLETE_MODEL_JSON_FILE_NAME = 'complete_data_model.json'

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
        return {LaserShockGlassID :self.glass_IDs,
                LaserShockFoilID : self.foil_IDs,
                LaserShockEpoxyID :self.epoxy_IDs,
                LaserShockSpacerID : self.spacer_IDs,
                LaserShockFlyerCuttingProgram : self.flyer_cutting_programs,
                LaserShockSpacerCuttingProgram : self.spacer_cutting_programs,
                LaserShockFlyerStack : self.flyer_stacks,
                LaserShockSample : self.samples,
                LaserShockLaunchPackage : self.launch_packages,
                LaserShockExperiment : self.experiments,
            }
    
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
        #read any json files in the directory and make sure there aren't any objects whose references are missing
        self.__check_json_uids()
        #initialize empty object lists
        self.glass_IDs = []
        self.foil_IDs = []
        self.epoxy_IDs = []
        self.spacer_IDs = []
        self.flyer_cutting_programs = []
        self.spacer_cutting_programs = []
        self.flyer_stacks = []
        self.samples = []
        self.launch_packages = []
        self.experiments = []
        #start up the template and spec stores
        self._template_store = GEMDTemplateStore(self.encoder)
        self._spec_store = GEMDSpecStore(self.encoder)
        #deserialize the data model from the single file
        self.__uids_written = []
        self.__deserialize_existing_model()
        #add any hardcoded templates that weren't deserialized to the template store
        self._template_store.add_missing_hardcoded_templates(ATTR_TEMPL,OBJ_TEMPL)
        msg = f'Template store initialized with {self._template_store.n_hardcoded} hardcoded templates and '
        msg+= f'{self._template_store.n_from_files} templates read from files in {self.dirpath}'
        self.logger.info(msg)
        msg=f'Spec store initialized with {self._spec_store.n_specs} specs read from an existing model'
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
        self.get_objects_from_records(LaserShockGlassID,self.glass_IDs,'Glass ID',**extra_kwargs)
        self.logger.debug(f'There are {len(self.glass_IDs)} Glass ID objects')
        self.get_objects_from_records(LaserShockFoilID,self.foil_IDs,'Foil ID',**extra_kwargs)
        self.logger.debug(f'There are {len(self.foil_IDs)} Foil ID objects')
        self.get_objects_from_records(LaserShockEpoxyID,self.epoxy_IDs,'Epoxy ID',**extra_kwargs)
        self.logger.debug(f'There are {len(self.epoxy_IDs)} Epoxy ID objects')
        self.get_objects_from_records(LaserShockSpacerID,self.spacer_IDs,'Spacer ID',**extra_kwargs)
        self.logger.debug(f'There are {len(self.spacer_IDs)} Spacer ID objects')
        self.get_objects_from_records(LaserShockFlyerCuttingProgram,self.flyer_cutting_programs,
                                      'Flyer Cutting Program',**extra_kwargs)
        self.logger.debug(f'There are {len(self.flyer_cutting_programs)} Flyer Cutting Program objects')
        self.get_objects_from_records(LaserShockSpacerCuttingProgram,self.spacer_cutting_programs,
                                      'Spacer Cutting Program',**extra_kwargs)
        self.logger.debug(f'There are {len(self.spacer_cutting_programs)} Spacer Cutting Program objects')
        #Flyer Stacks (Materials)
        self.logger.debug('Creating Flyer Stacks...')
        self.get_objects_from_records(LaserShockFlyerStack,self.flyer_stacks,'Flyer Stack',
                                      self.glass_IDs,self.foil_IDs,self.epoxy_IDs,self.flyer_cutting_programs,
                                      **extra_kwargs)
        self.logger.debug(f'There are {len(self.flyer_stacks)} Flyer Stack objects')
        #Samples (Materials)
        self.logger.debug('Creating Samples...')
        self.get_objects_from_records(LaserShockSample,self.samples,'Sample',**extra_kwargs)
        self.logger.debug(f'There are {len(self.samples)} Sample objects')
        #Launch packages (Materials)
        self.logger.debug('Creating Launch Packages...')
        self.get_objects_from_records(LaserShockLaunchPackage,self.launch_packages,'Launch Package',
                                      self.flyer_stacks,self.spacer_IDs,self.spacer_cutting_programs,self.samples,
                                      **extra_kwargs)
        self.logger.debug(f'There are {len(self.launch_packages)} Launch Package objects')
        #Experiments (Measurements)
        self.logger.debug('Creating Experiments...')
        self.get_objects_from_records(LaserShockExperiment,self.experiments,'Experiment',self.launch_packages,
                                      **extra_kwargs)
        self.logger.debug(f'There are {len(self.experiments)} Experiment objects')
        #remove any abandoned specs from the store
        n_specs_removed = 0
        to_remove = []
        self.__uids_needed = set()
        for obj_list in self.all_object_lists.values() :
            for obj in obj_list :
                recursive_foreach(obj,self.find_needed_uids)
        for spec in self._spec_store.all_specs :
            if spec.uids[self.encoder.scope] not in self.__uids_needed :
                to_remove.append(spec)
                #print(f'UID not needed: {type(spec).__name__} with name {spec.name} ({spec.uids[self.encoder.scope]})')
            #else :
                #print(f'UID needed: {type(spec).__name__} with name {spec.name} ({spec.uids[self.encoder.scope]})')
        for spec in to_remove :
            self._spec_store.remove_unneeded_spec(spec)
            n_specs_removed+=1
        if n_specs_removed>0 :
            self.logger.debug(f'Removed {n_specs_removed} unneeded Specs from the store')
        self.logger.debug(f'{self._spec_store.n_specs} total unique Specs stored')
        self.logger.info('Done creating GEMD objects')

    def find_needed_uids(self,item) :
        if isinstance_spec(item) :
            if self.encoder.scope not in item.uids.keys() :
                errmsg = f'Found a {type(item).__name__} with name {item.name} that has no UID set! object:\n{item}'
                raise RuntimeError(errmsg)
            else :
                self.__uids_needed.add(item.uids[self.encoder.scope])
    
    def get_objects_from_records(self,obj_type,obj_list,layout_name,*args,n_max_records=100000,records_dict=None,**kwargs) :
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
        if records_dict is not None :
            #get records from the dictionary
            all_records = records_dict[layout_name]
        else :
            #get records from the FileMaker server
            all_records = self.__get_filemaker_records(layout_name,n_max_records)
        #get recordId/modId pairs for all existing objects of this type that are in the directory already
        #and register them to the object index to rebuild their links
        existing_rec_mod_ids = {}
        for obj in obj_list :
            try :
                rec_id = get_tag_value_from_list(obj.tags,'recordId')
                mod_id = get_tag_value_from_list(obj.tags,'modId')
            except Exception as e :
                errmsg = f'ERROR: failed to get record/modIds for {obj_type} {obj.name}! Will reraise exception.'
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
        created_objs = []
        for ir,record in enumerate(records_to_use) :
            if ir>0 and ir%25==0 :
                self.logger.debug(f'\tCreating {obj_type.__name__} {ir} of {len(records_to_use)}...')
            created_obj = obj_type(record,*args,
                                         templates=self._template_store,
                                         specs=self._spec_store,
                                         logger=self.logger,**kwargs)
            created_objs.append(created_obj)
        if len(created_objs)>0 :
            self.__check_unique_values(created_objs)
        for obj in created_objs :
            obj_list.append(obj.gemd_object)

    def dump_to_json_files(self,n_max_objs=-1,complete_histories=False,indent=None,recursive=True,whole_model=True) :
        """
        Write out GEMD object json files
        
        n_max_objs = the maximum number of objects of each type to dump to json files
            (default = -1 writes out all new objects)
        complete_histories = if True, complete material histories are written out for any
            MaterialRunFromFileMakerRecord objects (default = False)
        indent = the indent to use when the files are written out (argument to json.dump). 
            Default results in most compact representation
        recursive = if True, also write out json files for all objects linked to each chosen object
        whole_model = if True, the entire model is written out to a single file that can be deserialized
        """
        self.logger.info('Dumping GEMD objects to JSON files...')
        #set a variable so the recursive function knows how to dump the files
        self.__indent = indent
        #dump the different "run" parts of the lab data model to json files
        for obj_type,obj_list in self.all_object_lists.items() :
            objs_to_dump = obj_list[:min(n_max_objs,len(obj_list))] if n_max_objs>0 else obj_list
            for obj in objs_to_dump :
                #skip any objects whose uids have already been written
                if self.encoder.scope in obj.uids.keys() and obj.uids[self.encoder.scope] in self.__uids_written :
                    continue
                fn = f'{obj_type.__name__}_recordId_{get_tag_value_from_list(obj.tags,"recordId")}.json'
                with open(self.dirpath/fn,'w') as fp :
                    fp.write(self.encoder.thin_dumps(obj,indent=indent))
                if complete_histories :
                    if isinstance_material_run(obj) :
                        context_list = complete_material_history(obj)
                        with open(self.dirpath/fn.replace('.json','_material_history.json'),'w') as fp :
                            fp.write(json.dumps(context_list,indent=indent))
                self.__uids_written.append(obj.uids[self.encoder.scope])
                if recursive :
                    recursive_foreach(obj,self.__dump_run_objs_to_json)
        #dump the specs in the spec store
        for spec in self._spec_store.all_specs :
            self.__dump_obj_to_json(spec)
        #dump the templates in the template store
        for template in self._template_store.all_templates :
            self.__dump_obj_to_json(template)
        #dump the entire data model out to a single file so it can be deserialized
        if whole_model :
            all_objs = []
            for template in self._template_store.all_templates :
                all_objs.append(template)
            for spec in self._spec_store.all_specs :
                all_objs.append(spec)
            for obj_list in self.all_object_lists.values() :
                for obj in obj_list :
                    all_objs.append(obj)
            with open(self.dirpath/COMPLETE_MODEL_JSON_FILE_NAME,'w') as fp :
                fp.write(self.encoder.dumps(all_objs,indent=indent))
        self.logger.info('Done.')

    #################### PRIVATE HELPER FUNCTIONS ####################

    def __check_json_uids(self) :
        uids_found = set()
        uids_referenced = set()
        for fp in self.dirpath.glob('*.json') :
            if fp.name==COMPLETE_MODEL_JSON_FILE_NAME :
                continue
            with open(fp,'r') as ofp :
                obj = self.encoder.raw_loads(ofp.read())
            uids_found.add(obj.uids[self.encoder.scope])
        for fp in self.dirpath.glob('*.json') :
            with open(fp,'r') as ofp :
                obj = self.encoder.raw_loads(ofp.read())
            self.__add_referenced_uids(obj,uids_referenced)
        msg = f'found {len(uids_found)} total objects with {len(uids_referenced)} '
        msg+= f'UIDs referenced in {self.dirpath}'
        self.logger.info(msg)
        missing_uids = set()
        for uid_referenced in uids_referenced :
            if uid_referenced not in uids_found :
                missing_uids.add(uid_referenced)
        if len(missing_uids)>0 :
            errmsg = f'ERROR: could not find objects corresponding to {len(missing_uids)} referenced UIDs in the json '
            errmsg+= f'files in {self.dirpath}:\n'
            for missing_uid in missing_uids :
                errmsg+=f'\t{missing_uid}\n'
            self.logger.error(errmsg,RuntimeError)

    def __add_referenced_uids(self,item,uids_referenced) :
        if isinstance_link_by_uid(item) :
            if item.scope==self.encoder.scope :
                uids_referenced.add(item.id)
        elif isinstance_list_or_tuple(item):
            for v in item :
                self.__add_referenced_uids(v,uids_referenced)
        elif isinstance_dict_serializable(item):
            for k,v in item.as_dict().items() :
                self.__add_referenced_uids(v,uids_referenced)

    def __deserialize_existing_model(self) :
        complete_model_fp = self.dirpath/COMPLETE_MODEL_JSON_FILE_NAME
        if not complete_model_fp.is_file() :
            warnmsg = 'WARNING: Deserialization of previously-created objects will be skipped '
            warnmsg+= f'because {complete_model_fp} does not exist'
            self.logger.warning(warnmsg)
            return
        #get absolutely all of the objects from the single data model file
        with open(complete_model_fp,'r') as fp :
            all_objs = self.encoder.load(fp)
        self.logger.info(f'Read {len(all_objs)} objects from {complete_model_fp}')
        uids_added = set()
        for obj in all_objs :
            #get the UID to only add each object one time
            if self.encoder.scope not in obj.uids.keys() :
                errmsg = f'ERROR: {type(obj).__name__} {obj.name} is missing a UID for scope "{self.encoder.scope}"!'
                self.logger.error(errmsg,RuntimeError)
            uid = obj.uids[self.encoder.scope]
            if uid in uids_added :
                continue
            #if it's a special-type object, add it to the list for the lab
            try :
                object_type = get_tag_value_from_list(obj.tags,'ObjectType')
            except ValueError :
                object_type=None
            if object_type is not None :
                for obj_type,obj_list in self.all_object_lists.items() :
                    if obj_type.__name__==object_type :
                        #print(f'Adding a {type(obj).__name__} {obj.name} object with uid {uid} to the list of {obj_type.__name__} objects')
                        obj_list.append(obj)
            #register any templates
            if isinstance_template(obj) :
                self._template_store.register_new_template_from_file(obj)
            #register any specs
            elif isinstance_spec(obj) :
                self._spec_store.register_new_unique_spec_from_file(obj)
            #add the UID to make sure the file won't be written out again by accident
            uids_added.add(uid)
            self.__uids_written.append(uid)
    
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
                            api_version='v1',
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
        uid = item.uids[self.encoder.scope]
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
