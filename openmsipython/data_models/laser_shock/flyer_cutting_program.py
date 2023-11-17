# imports
from gemd.entity.value import NominalCategorical, NominalReal, NominalInteger
from openmsipython.data_models.spec_from_filemaker_record import (
    ProcessSpecFromFileMakerRecord,
)


class LaserShockFlyerCuttingProgram(ProcessSpecFromFileMakerRecord):
    """
    GEMD representation of the process of cutting flyers using a femtosecond laser or laser cutter
    """

    name_key = "Program name"
    notes_key = "Description"

    @property
    def template(self):
        return self.templates.obj("Flyer Cutting Program")

    @property
    def tags_keys(self):
        return [*super().tags_keys, "Flyer Cutting ID", "Version Date"]

    @property
    def file_links_dicts(self):
        return [*super().file_links_dicts, {"filename": "Program Filename"}]

    @property
    def condition_dict(self):
        return {
            "Cutting Method": {
                "valuetype": NominalCategorical,
                "template": self.templates.attr("Cutting Method"),
            },
            "Typical Cutting Time": {
                "valuetype": NominalReal,
                "datatype": float,
                "template": self.templates.attr("Typical Cutting Time"),
            },
            "Cutting Tool": {
                "valuetype": NominalCategorical,
                "template": self.templates.attr("Cutting Tool"),
            },
        }

    @property
    def parameter_dict(self):
        return {
            "Laser Cutting Energy": {
                "valuetype": NominalReal,
                "datatype": float,
                "template": self.templates.attr("Laser Cutting Energy"),
            },
            "Number of Passes": {
                "valuetype": NominalInteger,
                "datatype": int,
                "template": self.templates.attr("Number of Passes"),
            },
            "Aperture Setting": {
                "valuetype": NominalCategorical,
                "template": self.templates.attr("Aperture Setting"),
            },
            "Depth of Cut": {
                "valuetype": NominalCategorical,
                "template": self.templates.attr("Depth of Cut"),
            },
        }

    @property
    def unique_values(self):
        return {
            **super().unique_values,
            "Flyer Cutting ID": self.get_tag_value("FlyerCuttingID"),
        }
