#imports
from gemd.entity.value import NominalCategorical, NominalReal
from ..spec_from_filemaker_record import MaterialSpecFromFileMakerRecord

class LaserShockFoilID(MaterialSpecFromFileMakerRecord) :
    """
    GEMD representation of a type of glass used in the Laser Shock Lab as a Material Spec
    """

    name_key = 'Foil Name'
    notes_key = 'Description'

    @property
    def template(self) :
        return self.templates.obj('Foil ID')

    @property
    def process_template(self) :
        return self.templates.obj('Purchasing Foil')

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Foil ID']

    @property
    def property_dict(self) :
        return {'Foil Thickness':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':self.templates.attr('Foil Thickness')},
                'Foil Length':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':self.templates.attr('Foil Length')},
                'Foil Width':{'valuetype':NominalReal,
                                   'datatype':float,
                                   'template':self.templates.attr('Foil Width')},
                'Foil Hardness':{'valuetype':NominalCategorical,
                                   'datatype':str,
                                   'template':self.templates.attr('Foil Hardness')},
                'Foil Material':{'valuetype':NominalCategorical,
                                   'datatype':str,
                                   'template':self.templates.attr('Foil Material')},
            }

    @property
    def process_parameter_dict(self) :
        return {'Foil Supplier':{'valuetype':NominalCategorical,
                                  'template':self.templates.attr('Foil Supplier')},
                'Foil Part Number':{'valuetype':NominalCategorical,
                                     'template':self.templates.attr('Foil Part Number')},
            }

    @property
    def unique_values(self):
        return {**super().unique_values,'Foil ID':self.get_tag_value('FoilID')}

    def ignore_key(self,key) :
        if key in ['Foil Picture'] :
            return True
        return super().ignore_key(key)