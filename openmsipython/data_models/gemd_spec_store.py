#imports
import pathlib
from typing import Union
from dataclasses import dataclass
from gemd.util.impl import set_uuids
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.json import GEMDJson
from .utilities import get_json_filename_for_gemd_object

@dataclass
class GEMDSpec :
    spec : Union[MaterialSpec,ProcessSpec,IngredientSpec,MeasurementSpec]
    as_dict_no_uid : dict
    filepath : pathlib.Path 

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
            new_spec_dict[new_name][new_uid] = GEMDSpec(new_spec,new_spec_as_dict_no_uid,fp)
