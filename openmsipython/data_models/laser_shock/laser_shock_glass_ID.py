#imports
from gemd.entity.value import DiscreteCategorical, NominalReal
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .spec_from_filemaker_record import MaterialSpecFromFileMakerRecord

class LaserShockGlassID(MaterialSpecFromFileMakerRecord) :
    """
    GEMD representation of a type of glass used in the Laser Shock Lab as a Material Spec
    """

    template = OBJ_TEMPL['Glass ID']
    process_template = OBJ_TEMPL['Purchasing Glass']
    name_key = 'Glass name'
    notes_key = 'Description'

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Glass ID']

    def ignore_key(self,key) :
        if key in ['Glass Picture'] :
            return True
        return super().ignore_key(key)

    @property
    def property_dict(self) :
        return {'Glass Thickness':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':ATTR_TEMPL['Glass Thickness']},
                'Glass Length':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':ATTR_TEMPL['Glass Length']},
                'Glass Width':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':ATTR_TEMPL['Glass Width']},
            }

    @property
    def process_parameter_dict(self) :
        return {'Glass Supplier':{'valuetype':DiscreteCategorical,
                                  'template':ATTR_TEMPL['Glass Supplier']},
                'Glass Part Number':{'valuetype':DiscreteCategorical,
                                     'template':ATTR_TEMPL['Glass Part Number']},
            }
