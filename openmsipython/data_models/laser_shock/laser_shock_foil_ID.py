#imports
from gemd.entity.value import NominalCategorical, NominalReal
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .spec_from_filemaker_record import MaterialSpecFromFileMakerRecord

class LaserShockFoilID(MaterialSpecFromFileMakerRecord) :
    """
    GEMD representation of a type of glass used in the Laser Shock Lab as a Material Spec
    """

    template = OBJ_TEMPL['Foil ID']
    process_template = OBJ_TEMPL['Purchasing Foil']
    name_key = 'Foil Name'
    notes_key = 'Description'

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Foil ID']

    def ignore_key(self,key) :
        if key in ['Foil Picture'] :
            return True
        return super().ignore_key(key)

    @property
    def property_dict(self) :
        return {'Foil Thickness':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':ATTR_TEMPL['Foil Thickness']},
                'Foil Length':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':ATTR_TEMPL['Foil Length']},
                'Foil Width':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':ATTR_TEMPL['Foil Width']},
                'Foil Hardness':{'valuetype':NominalCategorical,
                                   'datatype':str,
                                   'template':ATTR_TEMPL['Foil Hardness']},
                'Foil Material':{'valuetype':NominalCategorical,
                                   'datatype':str,
                                   'template':ATTR_TEMPL['Foil Material']},
            }

    @property
    def process_parameter_dict(self) :
        return {'Foil Supplier':{'valuetype':NominalCategorical,
                                  'template':ATTR_TEMPL['Foil Supplier']},
                'Foil Part Number':{'valuetype':NominalCategorical,
                                     'template':ATTR_TEMPL['Foil Part Number']},
            }

    @property
    def unique_values(self):
        return {**super().unique_values,'Foil ID':self.get_tag_value('FoilID')}