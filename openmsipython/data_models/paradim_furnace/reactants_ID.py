#imports
from gemd import NominalComposition
from gemd.entity.value import NominalCategorical, NominalReal
from ..spec_from_filemaker_record import MaterialSpecFromFileMakerRecord

class ReactantsID(MaterialSpecFromFileMakerRecord) :
    """
    GEMD representation of the reactants put into the furnace as a Material Spec
    """

    name_key = 'Reactants Name'
    notes_key = 'Description'

    @property
    def template(self) :
        return self.templates.obj('Reactants')

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Reactants']

    @property
    def property_dict(self) :
        return {'Reactants Formula':{'valuetype':NominalComposition,
                                   'template':self.templates.attr('Reactants Formula')},
            }

    @property
    def unique_values(self):
        return {**super().unique_values,'Reactants':self.get_tag_value('Reactants')}

    def ignore_key(self,key) :
        if key in ['Foil Picture'] :
            return True
        return super().ignore_key(key)