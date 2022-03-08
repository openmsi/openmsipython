#imports
import copy
from typing import Union
from dataclasses import dataclass
from gemd.util.impl import set_uuids
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.json import GEMDJson

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
        self.__material_spec_dict = self.__get_existing_specs_of_type(MaterialSpec)
        self.__process_spec_dict = self.__get_existing_specs_of_type(ProcessSpec)
        self.__ingredient_spec_dict = self.__get_existing_specs_of_type(IngredientSpec)
        self.__measurement_spec_dict = self.__get_existing_specs_of_type(MeasurementSpec)
        self.__types_to_dicts = {
            MaterialSpec : self.__material_spec_dict,
            ProcessSpec : self.__process_spec_dict,
            IngredientSpec : self.__ingredient_spec_dict,
            MeasurementSpec : self.__measurement_spec_dict,
        }

    def unique_version_of(self,specobj,debug=False) :
        """
        Returns a unique version of specobj by searching through the currently defined specs.
        If an already-existing object is identical to specobj, returns that object. 
        If specobj is unique w.r.t. what's already existing then that object is registered in the store and returned.

        specobj = the Spec object that should be registered or replaced with its corresponding unique object
        debug = True to print debugging statements
        """
        new_spec_name = specobj.name
        #get the dictionary of the new object before it has uids added
        new_spec_as_dict_no_uid = copy.deepcopy(specobj.as_dict())
        #figure out the dictionary of objects to search through based on the type and name of the spec
        dict_of_type = self.__types_to_dicts[type(specobj)]
        #search through all the objects matching type/name and if an identical one is found return that
        if new_spec_name in dict_of_type.keys() :
            dict_to_search = dict_of_type[new_spec_name]
            for existingspec in dict_to_search.values() :
                if existingspec.as_dict_no_uid==new_spec_as_dict_no_uid :
                    if debug :
                        print(f'Returning an existing {type(specobj)} with name {new_spec_name}')
                    return existingspec.spec
        else :
            dict_of_type[new_spec_name] = {}
        #if this spec doesn't already exist, add it to the store
        if debug :
            print(f'Creating a new {type(specobj)} with name {new_spec_name}')
        set_uuids(specobj,self.encoder.scope)
        new_uid = specobj.uids[self.encoder.scope]
        dict_of_type[new_spec_name][new_uid] = GEMDSpec(specobj,new_spec_as_dict_no_uid)
        self.__n_specs+=1
        #if this spec is a process, tunnel into its ingredients and output material as well to register them
        if type(specobj)==ProcessSpec :
            for ing in specobj.ingredients :
                _ = self.unique_version_of(ing)
            if specobj.output_material is not None :
                _ = self.unique_version_of(specobj.output_material)
        return specobj

    def __get_existing_specs_of_type(self,spec_type) :
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
