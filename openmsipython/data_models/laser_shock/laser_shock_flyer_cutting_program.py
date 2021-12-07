#imports
from gemd.entity.value import NominalCategorical, NominalReal, NominalInteger
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .spec_from_filemaker_record import ProcessSpecFromFileMakerRecord

class LaserShockFlyerCuttingProgram(ProcessSpecFromFileMakerRecord) :
    """
    GEMD representation of the process of cutting flyers using a femtosecond laser or laser cutter
    """

    template = OBJ_TEMPL['Flyer Cutting Program']
    name_key = 'Program name'
    notes_key = 'Description'

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Flyer Cutting ID','Version Date']

    @property
    def file_links_dicts(self) :
        return [*super().file_links_dicts,{'filename':'Program Filename'}]

    @property
    def condition_dict(self) :
        return {
            'Cutting Method':{'valuetype':NominalCategorical,
                              'template':ATTR_TEMPL['Cutting Method']},
            'Typical Cutting Time':{'valuetype':NominalReal,
                                    'datatype':float,
                                    'template':ATTR_TEMPL['Typical Cutting Time']},
            'Cutting Tool':{'valuetype':NominalCategorical,
                            'template':ATTR_TEMPL['Cutting Tool']},
        }

    @property
    def parameter_dict(self) :
        return {
            'Laser Cutting Energy':{'valuetype':NominalReal,
                                    'datatype':float,
                                    'template':ATTR_TEMPL['Laser Cutting Energy']},
            'Number of Passes':{'valuetype':NominalInteger,
                                'datatype':int,
                                'template':ATTR_TEMPL['Number of Passes']},
            'Aperture Setting':{'valuetype':NominalCategorical,
                                'template':ATTR_TEMPL['Aperture Setting']},
            'Depth of Cut':{'valuetype':NominalCategorical,
                            'template':ATTR_TEMPL['Depth of Cut']},
        }

    @property
    def unique_values(self):
        return {**super().unique_values,'Flyer Cutting ID':self.get_tag_value('FlyerCuttingID')}

