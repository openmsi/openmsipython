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

    def unique_version_of(self,specobj,debug=False,register=True) :
        """
        Returns a unique version of specobj by searching through the currently defined specs.
        If an already-existing object is identical to specobj, returns that object. 
        If specobj is unique w.r.t. what's already existing then that object is registered in the store and returned.

        specobj = the Spec object that should be registered or replaced with its corresponding unique object
        debug = True to print debugging statements
        register = True if the object should be added to the store if it's found to be unique
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
                    #check the ingredients and output materials of processes as well
                    if type(specobj)==ProcessSpec :
                        ex_om = existingspec.spec.output_material
                        new_om = specobj.output_material
                        if (ex_om is None) != (new_om is None) :
                            if debug :
                                print(f'output material type mismatched {ex_om} vs. {new_om}')
                            continue
                        ex_om_ad = (self.__mat_specs[ex_om.name][ex_om.uids[self.encoder.scope]]).as_dict_no_uid
                        new_om_ad = new_om.as_dict()
                        outputs_match = True
                        for (exk,exv),(nk,nv) in zip(ex_om_ad.items(),new_om_ad.items()) :
                            if (exk==nk) and nk in ('uids','process') :
                                continue
                            if exk!=nk or exv!=nv :
                                if debug :
                                    print(f'output materials mismatched {exk}={exv} vs. {nk}={nv}')
                                outputs_match = False
                                break
                        if not outputs_match :
                            continue
                        if len(specobj.ingredients)!=len(existingspec.spec.ingredients) :
                            if debug :
                                print('number of ingredients mismatched')
                            continue
                        ingredients_match=True
                        for ex_ing,new_ing in zip(existingspec.spec.ingredients,specobj.ingredients) :
                            ex_ing_ad = (self.__ing_specs[ex_ing.name][ex_ing.uids[self.encoder.scope]]).as_dict_no_uid
                            new_ing_ad = new_ing.as_dict()
                            for (exk,exv),(nk,nv) in zip(ex_ing_ad.items(),new_ing_ad.items()) :
                                if exk!=nk :
                                    if debug :
                                        print(f'ingredient mismatched {exk} vs. {nk}')
                                    ingredients_match = False
                                    break
                                if nk in ('uids','process') :
                                    continue
                                elif nk=='material' and (exv is not None or nv is not None) :
                                    ex_im_ad = (self.__mat_specs[exv.name][exv.uids[self.encoder.scope]]).as_dict_no_uid
                                    new_im_ad = nv.as_dict()
                                    ing_mats_match = True
                                    for (exk2,exv2),(nk2,nv2) in zip(ex_im_ad.items(),new_im_ad.items()) :
                                        if (exk2==nk2) and nk2 in ('uids','process') :
                                            continue
                                        if exk2!=nk2 or exv2!=nv2 :
                                            if debug :
                                                print(f'ingredient materials mismatched {exk2}={exv2} vs. {nk2}={nv2}')
                                            ing_mats_match = False
                                            break
                                    if not ing_mats_match :
                                        ingredients_match = False
                                        break
                                elif exk!=nk or exv!=nv :
                                    if debug :
                                        print(f'ingredient mismatched {exk}={exv} vs. {nk}={nv}')
                                    ingredients_match = False
                                    break
                            if not ingredients_match :
                                break
                        if not ingredients_match :
                            continue
                    if debug :
                        print(f'Returning an existing {type(specobj)} with name {new_spec_name}')
                    return existingspec.spec
        else :
            dict_of_type[new_spec_name] = {}
        #if this spec doesn't already exist, add it to the store
        if register : 
            if debug :
                print(f'Creating a new {type(specobj)} with name {new_spec_name}')
            set_uuids(specobj,self.encoder.scope)
            new_uid = specobj.uids[self.encoder.scope]
            dict_of_type[new_spec_name][new_uid] = GEMDSpec(specobj,new_spec_as_dict_no_uid)
            self.__n_specs+=1
            #if this spec is a process, tunnel into its ingredients and output material as well to register them
            if type(specobj)==ProcessSpec :
                for ing in specobj.ingredients :
                    _ = self.unique_version_of(ing,debug)
                    if ing.material is not None :
                        _ = self.unique_version_of(ing.material,debug)
                if specobj.output_material is not None :
                    _ = self.unique_version_of(specobj.output_material,debug)
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
