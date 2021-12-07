#imports
from gemd.entity.value import NominalCategorical
from ..spec_from_filemaker_record import MaterialSpecFromFileMakerRecord
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL

class LaserShockEpoxyID(MaterialSpecFromFileMakerRecord) :
    """
    GEMD representation of a type of Spacer used in the Laser Shock Lab as a Material Spec
    """
    
    template = OBJ_TEMPL['Epoxy ID']
    process_template = OBJ_TEMPL['Purchasing Epoxy']
    name_key = 'Epoxy Name'
    notes_key = 'Description'
    
    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Epoxy ID']

    @property
    def process_parameter_dict(self) :
        return {'Epoxy Supplier':{'valuetype':NominalCategorical,
                                  'template':ATTR_TEMPL['Epoxy Supplier']},
            }

    @property
    def unique_values(self):
        return {**super().unique_values,'Epoxy ID':self.get_tag_value('EpoxyID')}

    def ignore_key(self,key) :
        if key in ['Epoxy Picture'] :
            return True
        return super().ignore_key(key)
