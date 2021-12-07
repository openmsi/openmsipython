#imports
from gemd.entity.value import NominalCategorical, NominalReal
from ..spec_from_filemaker_record import MaterialSpecFromFileMakerRecord
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL

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
        return {'Glass Supplier':{'valuetype':NominalCategorical,
                                  'template':ATTR_TEMPL['Glass Supplier']},
                'Glass Part Number':{'valuetype':NominalCategorical,
                                     'template':ATTR_TEMPL['Glass Part Number']},
            }

    @property
    def unique_values(self):
        return {**super().unique_values,'Glass ID':self.get_tag_value('GlassID')}

    def ignore_key(self,key) :
        if key in ['Glass Picture'] :
            return True
        return super().ignore_key(key)
