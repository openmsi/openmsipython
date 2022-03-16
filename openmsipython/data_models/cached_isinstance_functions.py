#imports
from gemd.entity.link_by_uid import LinkByUID
from gemd.entity.dict_serializable import DictSerializable
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate
from gemd.entity.template import MaterialTemplate, ProcessTemplate, MeasurementTemplate
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun
from .utilities import cached_isinstance_generator

#Some cached isinstance functions to reduce overhead
isinstance_template = cached_isinstance_generator((PropertyTemplate, ParameterTemplate, ConditionTemplate,
                                                   MaterialTemplate, ProcessTemplate, MeasurementTemplate))
isinstance_spec = cached_isinstance_generator((MaterialSpec,ProcessSpec,IngredientSpec,MeasurementSpec))
isinstance_run = cached_isinstance_generator((MaterialRun,ProcessRun,IngredientRun,MeasurementRun))
isinstance_process_spec = cached_isinstance_generator(ProcessSpec)
isinstance_material_ingredient_spec = cached_isinstance_generator((MaterialSpec,IngredientSpec))
isinstance_ingredient_spec = cached_isinstance_generator(IngredientSpec)
isinstance_material_run = cached_isinstance_generator(MaterialRun)
isinstance_ingredient_run = cached_isinstance_generator(IngredientRun)
isinstance_link_by_uid = cached_isinstance_generator(LinkByUID)
isinstance_list_or_tuple = cached_isinstance_generator((list, tuple))
isinstance_dict_serializable = cached_isinstance_generator(DictSerializable)
