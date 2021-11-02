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
