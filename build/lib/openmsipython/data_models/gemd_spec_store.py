#imports
import copy, methodtools
from typing import Union
from dataclasses import dataclass
from gemd.util.impl import set_uuids, recursive_foreach
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.json import GEMDJson
from .cached_isinstance_functions import isinstance_spec

@dataclass
class GEMDSpec :
    spec : Union[MaterialSpec,ProcessSpec,IngredientSpec,MeasurementSpec]
    as_dict_no_uid : str
    from_file : bool

class GEMDSpecStore :
    """
    A class to hold and work with a set of GEMD spec objects. Allows easier loading from 
    a directory of json dump files coupled with dynamically-created specs
    """

    @property
    def n_specs(self) :
        return self.__n_specs
    @property
    def all_specs(self) :
        for specdict in self.__types_to_dicts.values() :
            for name in specdict.keys() :
                for uid in specdict[name].keys() :
                    yield specdict[name][uid].spec
    @property
    def all_read_specs(self) :
        for specdict in self.__types_to_dicts.values() :
            for name in specdict.keys() :
                for uid in specdict[name].keys() :
                    if specdict[name][uid].from_file :
                        yield specdict[name][uid].spec

    def __init__(self,encoder=GEMDJson(),debug=False) :
        self.encoder = encoder
        self.__n_specs = 0
        self.__mat_specs = {}
        self.__proc_specs = {}
        self.__ing_specs = {}
        self.__meas_specs = {}
        self.__types_to_dicts = {
            MaterialSpec : self.__mat_specs,
            ProcessSpec : self.__proc_specs,
            IngredientSpec : self.__ing_specs,
            MeasurementSpec : self.__meas_specs,
        }
        self.__debug=debug

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
        self.__debug = debug
        #check if an identical spec has been registered, and return it if so
        if recursive_check :
            if self.__spec_exists_in_store_rec(specobj) :
                return (self.__get_stored_version_of_spec(specobj,debug=debug)).spec
        else :
            existingspec = self.__get_stored_version_of_spec(specobj,debug=debug)
            if existingspec is not None :
                return existingspec.spec
        #if an existing spec wasn't returned, register this spec as a new one and then return it
        if recursive_register :
            recursive_foreach(specobj,self.__register_new_unique_specs,apply_first=True)
        else :
            self.__register_new_unique_specs(specobj)
        existingspec = self.__get_stored_version_of_spec(specobj,debug=debug)
        return existingspec.spec

    def register_new_unique_spec_from_file(self,item) :
        if not isinstance_spec(item) :
            return
        if self.__get_stored_version_of_spec(item) is not None :
            return
        self.__register_spec(item,from_file=True)

    def remove_unneeded_spec(self,item) :
        if not isinstance_spec(item) :
            return
        if self.encoder.scope not in item.uids.keys() :
            errmsg = f'ERROR: {type(item).__name__} {item.name} is missing a UID for scope "{self.encoder.scope}"'
            raise RuntimeError(errmsg)
        name = item.name
        uid = item.uids[self.encoder.scope]
        dict_to_use = self.__types_to_dicts[type(item)]
        if name not in dict_to_use.keys() :
            raise RuntimeError(f'ERROR: no {type(item).__name__} with name {name} found in spec store!')
        elif uid not in dict_to_use[name].keys() :
            raise RuntimeError(f'ERROR: no {type(item).__name__} {name} with UID {uid} found in spec store!')
        _ = dict_to_use[name].pop(uid)
        self.__n_specs-=1

    def __get_spec_dict_no_uids(self,specobj) :
        """
        Return a version of a Spec object serialized to a string representation of a 
        dictionary where all UIDs of the relevant encoder scope have been removed
        """
        spec_copy = copy.deepcopy(specobj)
        recursive_foreach(spec_copy,self.__scrub_uids)
        return str(spec_copy)

    def __scrub_uids(self,item) :
        if not isinstance_spec(item) :
            return
        if self.encoder.scope in item.uids.keys() :
            _ = item.uids.pop(self.encoder.scope)

    @methodtools.lru_cache(maxsize=256)
    def __get_name_and_dict_for_spec(self,specobj) :
        return specobj.name, self.__get_spec_dict_no_uids(specobj)

    def __get_stored_version_of_spec(self,specobj,debug=False) :
        new_spec_name, new_spec_as_dict_no_uid = self.__get_name_and_dict_for_spec(specobj)
        dict_of_type = self.__types_to_dicts[type(specobj)]
        if new_spec_name in dict_of_type.keys() :
            dict_to_search = dict_of_type[new_spec_name]
            if self.encoder.scope in specobj.uids.keys() :
                if specobj.uids[self.encoder.scope] in dict_to_search.keys() :
                    if debug :
                        msg = f'Returning an existing {type(specobj).__name__} with name {new_spec_name} '
                        msg+= f'({specobj.uids[self.encoder.scope]}) (found by UID)'
                        print(msg)
                    return dict_to_search[specobj.uids[self.encoder.scope]]
                return None
            for existingspec in dict_to_search.values() :
                if (existingspec.spec==specobj) :
                    if debug :
                        msg = f'Returning an existing {type(specobj).__name__} with name {new_spec_name} '
                        msg+= f'({existingspec.spec.uids[self.encoder.scope]}) (found by spec comp)'
                        print(msg)
                    return existingspec
                elif (existingspec.as_dict_no_uid==new_spec_as_dict_no_uid) :
                    if debug :
                        msg = f'Returning an existing {type(specobj).__name__} with name {new_spec_name} '
                        msg+= f'({existingspec.spec.uids[self.encoder.scope]}) '
                        msg+= '(found by dict comp)'#:{existingspec.as_dict_no_uid} and \n{new_spec_as_dict_no_uid})'
                        print(msg)
                    return existingspec
        return None

    def __spec_exists_in_store_rec(self,specobj) :
        self.__n_objs_searched = 0
        self.__n_objs_found = 0
        recursive_foreach(specobj,self.__check_spec_exists_in_store,apply_first=True)
        if self.__n_objs_searched==self.__n_objs_found :
            return True
        return False

    def __check_spec_exists_in_store(self,item) :
        if self.__n_objs_found<self.__n_objs_searched :
            return
        elif not isinstance_spec(item) :
            return
        self.__n_objs_searched+=1
        stored_version = self.__get_stored_version_of_spec(item)
        if stored_version is not None :
            self.__n_objs_found+=1

    def __register_new_unique_specs(self,item) :
        if not isinstance_spec(item) :
            return
        if self.__spec_exists_in_store_rec(item) :
            return
        self.__register_spec(item)

    def __register_spec(self,item,from_file=False) :
        new_spec_name, new_spec_as_dict_no_uid = self.__get_name_and_dict_for_spec(item)
        dict_of_type = self.__types_to_dicts[type(item)]
        if new_spec_name not in dict_of_type.keys() :
            dict_of_type[new_spec_name] = {}
        set_uuids(item,self.encoder.scope)
        new_uid = item.uids[self.encoder.scope]
        if self.__debug :
            print(f'Creating a new {type(item).__name__} with name {new_spec_name} ({new_uid})')
        dict_of_type[new_spec_name][new_uid] = GEMDSpec(item,new_spec_as_dict_no_uid,from_file)
        self.__n_specs+=1
    