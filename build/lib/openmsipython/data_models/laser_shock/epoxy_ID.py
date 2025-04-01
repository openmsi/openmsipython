#imports
from gemd.entity.value import NominalCategorical
from ..spec_from_filemaker_record import MaterialSpecFromFileMakerRecord

class LaserShockEpoxyID(MaterialSpecFromFileMakerRecord) :
    """
    GEMD representation of a type of Spacer used in the Laser Shock Lab as a Material Spec
    """

    name_key = 'Epoxy Name'
    notes_key = 'Description'
    
    @property
    def template(self) :
        return self.templates.obj('Epoxy ID')

    @property
    def process_template(self) :
        return self.templates.obj('Purchasing Epoxy')
    
    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Epoxy ID']

    @property
    def process_parameter_dict(self) :
        return {'Epoxy Supplier':{'valuetype':NominalCategorical,
                                  'template':self.templates.attr('Epoxy Supplier')},
            }

    @property
    def unique_values(self):
        return {**super().unique_values,'Epoxy ID':self.get_tag_value('EpoxyID')}

    def ignore_key(self,key) :
        if key in ['Epoxy Picture'] :
            return True
        return super().ignore_key(key)
