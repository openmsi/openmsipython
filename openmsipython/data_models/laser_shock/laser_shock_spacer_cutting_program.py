#imports
from gemd.entity.value import NominalCategorical, NominalReal
from gemd.entity.value.nominal_integer import NominalInteger
from .attribute_templates import ATTR_TEMPL
from .object_templates import OBJ_TEMPL
from .spec_from_filemaker_record import ProcessSpecFromFileMakerRecord

class LaserShockSpacerCuttingProgram(ProcessSpecFromFileMakerRecord) :
    """
    GEMD representation of the process of cutting spacers using a femtosecond laser or laser cutter
    """

    template = OBJ_TEMPL['Spacer Cutting Program']
    name_key = 'Program Name'
    notes_key = 'Spacer Description'

    @property
    def tags_keys(self) :
        return [*super().tags_keys,'Spacer Cutting ID','Version Date']

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

