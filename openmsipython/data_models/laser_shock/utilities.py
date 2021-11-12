#imports
from gemd.entity.value import NominalInteger, NominalReal, DiscreteCategorical
from gemd.entity.value.nominal_integer import NominalInteger

def search_for_single_name(obj_list,name) :
    """
    Search a given list of objects for exactly one of them with a name matching the given name
    If none are found in the list, returns None
    If more than one are found a RuntimeError is thrown 
    """
    obj = [o for o in obj_list if o.name==name]
    if len(obj)==0 :
        return None
    elif len(obj)==1 :
        return obj[0]
    elif len(obj)>1 :
        raise RuntimeError(f'ERROR: more than one objects were found matching name {name}: {obj}')

def search_for_single_tag(ent_list,tagname,tagvalue) :
    """
    Search a given list of entities for exactly one of them with 
    a tag matching the given tagname with value = the given tagvalue
    If none are found in the list, returns None
    If more than one are found a RuntimeError is thrown 
    """
    ents = []
    for ent in ent_list :
        for t in ent.tags :
            tsplit = t.split('::')
            if len(tsplit)!=2 :
                continue
            if tsplit[0]==tagname and tsplit[1]==tagvalue :
                ents.append(ent)
                break
    if len(ents)==0 :
        return None
    elif len(ents)==1 :
        return ents[0]
    elif len(ents)>1 :
        errmsg=f'ERROR: more than one entities were found matching name::value={tagname}::{tagvalue} : {ents}'
        raise RuntimeError(errmsg)

def name_value_template_from_key_value_dict(key,value,d) :
    """
    Given a FileMaker record key, its value, and a dictionary specifying 
    a valuetype, datatype, and template for the entry, return the name, 
    value, and template that should be added to some corresponding GEMD construct 
    """
    if value in ('','N/A') :
        return None, None, None
    name = key.replace(' ','')
    val = value
    if 'datatype' in d.keys() :
        val = d['datatype'](val)
    temp = None
    if 'template' in d.keys() :
        temp = d['template']
    if 'valuetype' not in d.keys() :
        raise ValueError(f'ERROR: no valuetype given for dict entry {key}!')
    elif d['valuetype']==NominalInteger :
        value = d['valuetype'](val)
    elif d['valuetype']==NominalReal :
        if 'template' not in d.keys() :
            raise ValueError(f'ERROR: no template given for NominalReal dict entry {key}!')
        value = d['valuetype'](val,temp.bounds.default_units)
    elif d['valuetype']==DiscreteCategorical :
        value = d['valuetype']({val:1.0})
    return name, value, temp