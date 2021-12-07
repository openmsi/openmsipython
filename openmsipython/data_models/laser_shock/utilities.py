#imports
from gemd.entity.value import NominalCategorical, NominalReal, NominalInteger

def search_for_name(obj_list,name) :
    """
    Filter a given list of objects for any that have a name matching the given name
    If none are found in the list, returns None
    """
    objs = [o for o in obj_list if o.name==name]
    if len(objs)==0 :
        return None
    return objs

def search_for_single_name(obj_list,name,logger=None,raise_exception=True) :
    """
    Search a given list of objects for exactly one of them with a name matching the given name
    If none are found in the list, returns None
    If more than one are found, a warning or error are sent to the logger (or just raised) 
    If only a warning is sent to the logger, then the first object found is returned
    """
    objs = search_for_name(obj_list,name)
    if objs is None or len(objs)==0 :
        return None
    elif len(objs)==1 :
        return objs[0]
    elif len(objs)>1 :
        msg = f'{len(objs)} objects were found matching name {name}'
        if logger is None :
            raise RuntimeError(f'ERROR: {msg}')
        else :
            if raise_exception :
                logger.error(msg,RuntimeError)
            else :
                msg+='. The first object found will be returned.'
                logger.warning(msg)
                return objs[0]

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

def name_value_template_origin_from_key_value_dict(key,value,d,logger=None,raise_exception=True) :
    """
    Given a FileMaker record key, its value, and a dictionary specifying 
    a valuetype, datatype, template, and origin for the entry, return the name, 
    value, template, and origin of the information that should be added to some corresponding GEMD construct 
    """
    if value in ('','N/A') :
        return None, None, None, None
    name = key.replace(' ','')
    val = value
    if 'datatype' in d.keys() :
        try :
            val = d['datatype'](val)
        except ValueError as e :
            msg = f'failed to cast {val} to {d["datatype"]}'
            if raise_exception :
                if logger is None :
                    raise e
                else :
                    logger.error(msg,ValueError)
            else :
                if logger is not None :
                    msg+='. Value added with no template and "CouldNotCast" appended to the name.'
                    logger.warning(msg)
                name+='CouldNotCast'
                val=str(val)
                d['valuetype'] = NominalCategorical
                d['template'] = None
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
    elif d['valuetype']==NominalCategorical :
        value = d['valuetype'](val)
    origin = d['origin'] if 'origin' in d.keys() else None
    return name, value, temp, origin
