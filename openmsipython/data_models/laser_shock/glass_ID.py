#imports
from gemd.entity.value import NominalCategorical, NominalReal
from ..spec_from_filemaker_record import MaterialSpecFromFileMakerRecord

class LaserShockGlassID(MaterialSpecFromFileMakerRecord) :
    """
    GEMD representation of a type of glass used in the Laser Shock Lab as a Material Spec
    """

    name_key = 'Glass name'
    notes_key = 'Description'

    @property
    def template(self) :
        return self.templates.obj('Glass ID')

    @property
    def process_template(self) :
        return self.templates.obj('Purchasing Glass')

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Glass ID']

    @property
    def property_dict(self) :
        return {'Glass Thickness':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':self.templates.attr('Glass Thickness')},
                'Glass Length':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':self.templates.attr('Glass Length')},
                'Glass Width':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':self.templates.attr('Glass Width')},
            }

    @property
    def process_parameter_dict(self) :
        return {'Glass Supplier':{'valuetype':NominalCategorical,
                                  'template':self.templates.attr('Glass Supplier')},
                'Glass Part Number':{'valuetype':NominalCategorical,
                                     'template':self.templates.attr('Glass Part Number')},
            }

    @property
    def unique_values(self):
        return {**super().unique_values,'Glass ID':self.get_tag_value('GlassID')}

    def ignore_key(self,key) :
        if key in ['Glass Picture'] :
            return True
        return super().ignore_key(key)
