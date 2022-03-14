#imports
from typing import Union
from dataclasses import dataclass
from gemd.util.impl import set_uuids, substitute_objects
from gemd.json import GEMDJson
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate
from gemd.entity.template import MaterialTemplate, MeasurementTemplate, ProcessTemplate
from .utilities import get_json_filename_for_gemd_object

@dataclass
class GEMDTemplate :
    template : Union[PropertyTemplate,ParameterTemplate,ConditionTemplate,
                     MaterialTemplate,MeasurementTemplate,ProcessTemplate]
    from_file : bool

class GEMDTemplateStore :
    """
    A class to hold and work with a set of GEMD template objects. Allows easier loading from 
    a directory of json dump files coupled with one or more dictionaries of static, hard-coded templates
    """

    @property
    def n_from_files(self) :
        return self.__n_from_files
    @property
    def n_hardcoded(self) :
        return self.__n_hardcoded
    @property
    def all_templates(self) :
        both_dicts = [self.__attribute_templates,self.__object_templates]
        for tempdict in both_dicts :
            for name in tempdict.keys() :
                yield tempdict[name].template
    @property
    def all_read_templates(self) :
        both_dicts = [self.__attribute_templates,self.__object_templates]
        for tempdict in both_dicts :
            for name in tempdict.keys() :
                if tempdict[name].from_file :
                    yield tempdict[name].template

    def __init__(self,dirpath,attr_hardcoded,obj_hardcoded,encoder=GEMDJson()) :
        """
        dirpath = Path to a directory that may hold some json dumps of GEMD objects corresponding to 
            some hard-coded templates
        attr_hardcoded = a dictionary of hard-coded attribute templates, some of which may have been 
            used previously and dumped as json into dirpath
        obj_hardcoded = a dictionary of hard-coded object templates, some of which may have been used 
            previously and dumped as json into dirpath
        encoder = a pre-created GEMD JSON encoder (optional)
        """
        self.encoder = encoder
        self.__n_from_files = 0
        self.__n_hardcoded = 0
        self.__attribute_templates = self.__get_template_dict(dirpath,attr_hardcoded)
        self.__object_templates = self.__get_template_dict(dirpath,obj_hardcoded)

    def attr(self,template_name) :
        """
        Return an attribute template given its name
        """
        try :
            return self.__attribute_templates[template_name].template
        except KeyError :
            raise ValueError(f'ERROR: no stored attribute template called "{template_name}"')

    def obj(self,template_name) :
        """
        Return an object template given its name
        """
        try :
            return self.__object_templates[template_name].template
        except KeyError :
            raise ValueError(f'ERROR: no stored object template called "{template_name}"')

    def substitute_objects(self,index_dict) :
        """
        Replace LinkByUID objects with pointers to the objects with that UID in the index_dict
        """
        for name,template in self.__attribute_templates.items() :
            new_template = substitute_objects(template.template,index_dict)
            self.__attribute_templates[name].template = new_template
        for name,template in self.__object_templates.items() :
            new_template = substitute_objects(template.template,index_dict)
            self.__object_templates[name].template = new_template

    def __get_template_dict(self,dirpath,hardcoded) :
        new_templates_dict = {}
        names_seen = set()
        for name,template in hardcoded.items() :
            if name in names_seen :
                raise ValueError(f'ERROR: harcoded template dictionary duplicates template name {name}!')
            else :
                names_seen.add(name)
            if template.uids is not None and self.encoder.scope in template.uids.keys() :
                errmsg = f'ERROR: "{self.encoder.scope}" scope UID has already been set for a hard-coded template!'
                raise RuntimeError(errmsg)
            filename_stem = (get_json_filename_for_gemd_object(template,self.encoder))[:-len('.json')]
            fps_found = []
            for fp in dirpath.glob(f'{filename_stem}_*json') :
                with open(fp,'r') as ofp :
                    new_template = self.encoder.raw_loads(ofp.read())
                if new_template.uids is None or self.encoder.scope not in new_template.uids.keys() :
                    errmsg = f'ERROR: template read from {fp} is missing a "{self.encoder.scope}" scope UID!'
                    raise RuntimeError(errmsg)
                else :
                    template.add_uid(self.encoder.scope,new_template.uids[self.encoder.scope])
                if template.as_dict()!=new_template.as_dict() :
                    errmsg = f'ERROR: hardcoded {template.__class__.__name__} template with name {name} is mismatched '
                    errmsg+= f'to template read from file at {fp}!'
                    raise RuntimeError(errmsg)
                new_templates_dict[name] = GEMDTemplate(new_template,True)
                fps_found.append(fp)
            if len(fps_found)>1 :
                errmsg = f'ERROR: found more than one filepath for template with name stem {filename_stem} '
                errmsg+= f'in {dirpath}: '
                for fp in fps_found :
                    errmsg+=f'\n{fp}'
                raise RuntimeError(errmsg)
            if name not in new_templates_dict.keys() :
                #print(f'No file found for {template.__class__.__name__} template with name {name}')
                set_uuids(template,self.encoder.scope)
                new_templates_dict[name] = GEMDTemplate(template,False)
                self.__n_hardcoded+=1
            else :
                self.__n_from_files+=1
        return new_templates_dict
