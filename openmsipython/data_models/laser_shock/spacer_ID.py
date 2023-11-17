# imports
from gemd.entity.value import NominalCategorical, NominalReal
from openmsipython.data_models.spec_from_filemaker_record import (
    MaterialSpecFromFileMakerRecord,
)


class LaserShockSpacerID(MaterialSpecFromFileMakerRecord):
    """
    GEMD representation of a type of Spacer used in the Laser Shock Lab as a Material Spec
    """

    name_key = "Spacer Name"
    notes_key = "Description"

    @property
    def template(self):
        return self.templates.obj("Spacer ID")

    @property
    def process_template(self):
        return self.templates.obj("Purchasing Spacer")

    @property
    def tags_keys(self):
        return [*super().tags_keys, "Spacer ID"]

    @property
    def property_dict(self):
        return {
            "Spacer Thickness": {
                "valuetype": NominalReal,
                "datatype": float,
                "template": self.templates.attr("Spacer Thickness"),
            },
            "Spacer Material": {
                "valuetype": NominalCategorical,
                "datatype": str,
                "template": self.templates.attr("Spacer Material"),
            },
            "Spacer Adhesive": {
                "valuetype": NominalCategorical,
                "datatype": str,
                "template": self.templates.attr("Spacer Adhesive Sides"),
            },
            "Adhesive Type": {
                "valuetype": NominalCategorical,
                "datatype": str,
                "template": self.templates.attr("Adhesive Type"),
            },
        }

    @property
    def process_parameter_dict(self):
        return {
            "Spacer Supplier": {
                "valuetype": NominalCategorical,
                "template": self.templates.attr("Spacer Supplier"),
            },
            "Spacer Part Number": {
                "valuetype": NominalCategorical,
                "template": self.templates.attr("Spacer Part Number"),
            },
        }

    @property
    def unique_values(self):
        return {**super().unique_values, "Spacer ID": self.get_tag_value("SpacerID")}

    def ignore_key(self, key):
        if key in ["Spacer Picture"]:
            return True
        return super().ignore_key(key)
