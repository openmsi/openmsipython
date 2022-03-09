#imports
import copy, methodtools
from typing import Union
from dataclasses import dataclass
from gemd.util.impl import set_uuids, recursive_foreach
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.json import GEMDJson
from pyparsing import RecursiveGrammarException
from .cached_isinstance_functions import isinstance_spec

@dataclass
class GEMDSpec :
    spec : Union[MaterialSpec,ProcessSpec,IngredientSpec,MeasurementSpec]
    as_dict_no_uid : dict

class GEMDSpecStore :
    """
    A class to hold and work with a set of GEMD spec objects. Allows easier loading from 
    a directory of json dump files coupled with dynamically-created specs
    """

    @property
    def n_specs(self) :
        return self.__n_specs

    def __init__(self,dirpath,encoder=GEMDJson()) :
        self.dirpath = dirpath
        self.encoder = encoder
        self.__n_specs = 0
        self.__mat_specs = self.__get_existing_specs_of_type(MaterialSpec)
        self.__proc_specs = self.__get_existing_specs_of_type(ProcessSpec)
        self.__ing_specs = self.__get_existing_specs_of_type(IngredientSpec)
        self.__meas_specs = self.__get_existing_specs_of_type(MeasurementSpec)
        self.__types_to_dicts = {
            MaterialSpec : self.__mat_specs,
            ProcessSpec : self.__proc_specs,
            IngredientSpec : self.__ing_specs,
            MeasurementSpec : self.__meas_specs,
        }

    def unique_version_of(self,specobj,debug=False,recursive_check=True,recursive_register=True) :
        """
        Returns a unique version of specobj by searching through the currently defined specs.
        If an already-existing object is identical to specobj, returns that object. 
        If specobj is unique w.r.t. what's already existing then that object is registered in the store and returned.

        specobj = the Spec object that should be registered or replaced with its corresponding unique object
        debug = True to print debugging statements
        recursive_check = True is any Spec objects linked to this object should also be checked for uniqueness
        recursive_register = True if any Spec objects linked to this object should be registered in the store
        """
        #check if an identical spec has been registered, and return it if so
        if recursive_check :
            self.__n_objs_searched = 0
            self.__n_objs_found = 0
            recursive_foreach(specobj,self.__check_spec_exists_in_store,apply_first=True)
            if self.__n_objs_searched==self.__n_objs_found :
                self.__n_objs_searched = 0
                self.__n_objs_found = 0
                return (self.__get_stored_version_of_spec(specobj,debug=debug)).spec
        else :
            existingspec = self.__get_stored_version_of_spec(specobj,debug=debug)
            if existingspec is not None :
                return existingspec.spec
        #if an existing spec wasn't returned, register this spec as a new one and then return it
        self.__debug = debug
        if recursive_register :
            recursive_foreach(specobj,self.__register_new_spec,apply_first=True)
        else :
            self.__register_new_spec(specobj)
        existingspec = self.__get_stored_version_of_spec(specobj,debug=debug)
        return existingspec.spec

    def __get_existing_specs_of_type(self,spec_type) :
        """
        Return a dictionary of spec objects of a certain type that exist in the directory
        """
        new_spec_dict = {}
        dicts_no_uid_seen = []
        filepaths_seen = []
        for fp in self.dirpath.glob(f'{spec_type.__name__}_*_*.json') :
            with open(fp,'r') as ofp :
                new_spec = self.encoder.raw_loads(ofp.read())
            if new_spec.uids is None or self.encoder.scope not in new_spec.uids.keys() :
                errmsg = f'ERROR: spec read from {fp} is missing a "{self.encoder.scope}" scope UID!'
                raise RuntimeError(errmsg)
            new_spec_as_dict_no_uid = new_spec.as_dict()
            _ = new_spec_as_dict_no_uid.pop('uids')
            for seen_dict,filepath in zip(dicts_no_uid_seen,filepaths_seen) :
                if new_spec_as_dict_no_uid==seen_dict :
                    errmsg = f'ERROR: {spec_type} spec read from {fp} is identical to spec read from {filepath}!'
                    raise RuntimeError(errmsg)
            dicts_no_uid_seen.append(new_spec_as_dict_no_uid)
            filepaths_seen.append(fp)
            new_name = new_spec.name
            if new_name not in new_spec_dict.keys() :
                new_spec_dict[new_name] = {}
            new_uid = new_spec.uids[self.encoder.scope]
            new_spec_dict[new_name][new_uid] = GEMDSpec(new_spec,new_spec_as_dict_no_uid)
            self.__n_specs+=1
        return new_spec_dict

    def __get_spec_dict_no_uids(self,specobj) :
        """
        Return a version of a Spec object serialized to a dictionary where all 
        UIDs of the relevant encoder scope have been removed
        """
        spec_as_dict = copy.deepcopy(specobj.as_dict())
        self.__scrub_uids_from_dict(spec_as_dict)
        return spec_as_dict

    def __scrub_uids_from_dict(self,d) :
        """
        Recursively remove UIDs of the relevant scope from a given dictionary
        """
        for key,value in d.items() :
            if key=='uids' and self.encoder.scope in value.keys() :
                _ = value.pop(self.encoder.scope)
            elif type(value)==dict :
                self.__scrub_uids_from_dict(value)

    @methodtools.lru_cache(maxsize=32)
    def __get_name_and_dict_for_spec(self,specobj) :
        return specobj.name, self.__get_spec_dict_no_uids(specobj)

    def __get_stored_version_of_spec(self,specobj,debug=False) :
        new_spec_name, new_spec_as_dict_no_uid = self.__get_name_and_dict_for_spec(specobj)
        #new_spec_as_dict_no_uid = copy.deepcopy(specobj.as_dict())
        dict_of_type = self.__types_to_dicts[type(specobj)]
        if new_spec_name in dict_of_type.keys() :
            dict_to_search = dict_of_type[new_spec_name]
            for existingspec in dict_to_search.values() :
                if (existingspec.spec==specobj) or (existingspec.as_dict_no_uid==new_spec_as_dict_no_uid) :
                    if debug :
                        print(f'Returning an existing {type(specobj)} with name {new_spec_name}')
                    return existingspec
        return None

    def __check_spec_exists_in_store(self,item) :
        if not isinstance_spec(item) :
            return
        self.__n_objs_searched+=1
        if self.__get_stored_version_of_spec(item) is not None :
            self.__n_objs_found+=1

    def __register_new_spec(self,item) :
        if not isinstance_spec(item) :
            return
        if self.__get_stored_version_of_spec(item) is not None :
            return
        new_spec_name, new_spec_as_dict_no_uid = self.__get_name_and_dict_for_spec(item)
        if self.__debug :
            print(f'Creating a new {type(item)} with name {new_spec_name}')
        dict_of_type = self.__types_to_dicts[type(item)]
        if new_spec_name not in dict_of_type.keys() :
            dict_of_type[new_spec_name] = {}
        set_uuids(item,self.encoder.scope)
        new_uid = item.uids[self.encoder.scope]
        dict_of_type[new_spec_name][new_uid] = GEMDSpec(item,new_spec_as_dict_no_uid)
        self.__n_specs+=1
    