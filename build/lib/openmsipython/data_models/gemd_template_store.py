#imports
from typing import Union
from dataclasses import dataclass
from gemd.util.impl import set_uuids
from gemd.json import GEMDJson
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate
from gemd.entity.template import MaterialTemplate, MeasurementTemplate, ProcessTemplate
from .cached_isinstance_functions import isinstance_template, isinstance_attribute_template, isinstance_object_template

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

    def __init__(self,encoder=GEMDJson()) :
        """
        encoder = a pre-created GEMD JSON encoder (optional)
        """
        self.encoder = encoder
        self.__n_from_files = 0
        self.__n_hardcoded = 0
        self.__attribute_templates = {}
        self.__object_templates = {}

    def register_new_template_from_file(self,template) :
        """
        Add a new template that's been read from a file
        """
        if not isinstance_template(template) :
            return
        name = template.name
        if self.encoder.scope not in template.uids.keys() :
            errmsg = f'ERROR: {type(template).__name__} {name} is missing a UID for scope "{self.encoder.scope}"!'
            raise RuntimeError(errmsg)
        dict_to_add_to = None
        if isinstance_attribute_template(template) :
            dict_to_add_to = self.__attribute_templates
        elif isinstance_object_template(template) :
            dict_to_add_to = self.__object_templates
        if dict_to_add_to is None :
            raise RuntimeError(f'ERROR: unrecognized template type {type(template)}!')
        if name in dict_to_add_to.keys() :
            raise RuntimeError(f'ERROR: template with name {name} already exists in store!')
        dict_to_add_to[name] = GEMDTemplate(template,True)
        self.__n_from_files+=1

    def add_missing_hardcoded_templates(self,attr_hardcoded,obj_hardcoded) :
        """
        Add any templates in the hardcoded dictionary that haven't already been added from a deserialization step

        attr_hardcoded = a dictionary of hard-coded attribute templates, some of which may have been 
            used previously and dumped as json into dirpath
        obj_hardcoded = a dictionary of hard-coded object templates, some of which may have been used 
            previously and dumped as json into dirpath
        """
        self.__add_missing_templates(attr_hardcoded)
        self.__add_missing_templates(obj_hardcoded)

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

    def __add_missing_templates(self,hardcoded) :
        names_seen = set()
        for name,template in hardcoded.items() :
            if name in names_seen :
                raise ValueError(f'ERROR: harcoded template dictionary duplicates template name {name}!')
            else :
                names_seen.add(name)
            if template.uids is not None and self.encoder.scope in template.uids.keys() :
                errmsg = f'ERROR: "{self.encoder.scope}" scope UID has already been set for a hard-coded template!'
                raise RuntimeError(errmsg)
            dict_to_add_to = None
            if isinstance_attribute_template(template) :
                dict_to_add_to = self.__attribute_templates
            elif isinstance_object_template(template) :
                dict_to_add_to = self.__object_templates
            if dict_to_add_to is None :
                raise RuntimeError(f'ERROR: unrecognized template type {type(template)}!')
            if name in dict_to_add_to.keys() :
                continue
            set_uuids(template,self.encoder.scope)
            dict_to_add_to[name] = GEMDTemplate(template,False)
            self.__n_hardcoded+=1
