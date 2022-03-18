#imports
from typing import Callable, Union, Type, Tuple
from gemd.entity.link_by_uid import LinkByUID
from gemd.entity.dict_serializable import DictSerializable
from gemd.entity.template import PropertyTemplate, ParameterTemplate, ConditionTemplate
from gemd.entity.template import MaterialTemplate, ProcessTemplate, MeasurementTemplate
from gemd.entity.object import MaterialSpec, ProcessSpec, IngredientSpec, MeasurementSpec
from gemd.entity.object import MaterialRun, ProcessRun, IngredientRun, MeasurementRun

######### THE FUNCTION BELOW IS COPIED/PASTED FROM GEMD CODE #########
def cached_isinstance_generator(class_or_tuple: Union[Type, Tuple[Type]]) -> Callable[[object], bool]:
    """
    Generate a function that checks and caches an isinstance(obj, class_or_tuple) call.

    Parameters
    ----------
    class_or_tuple: Union[Type, Tuple[Type]]
        A single type or a tuple of types

    Returns
    -------
    Callable[[object], bool]
        function with signature function(obj), returning isinstance(obj, class_or_tuple)

    """
    cache = dict()

    def func(obj):
        obj_type = type(obj)
        if obj_type not in cache:
            cache[obj_type] = isinstance(obj, class_or_tuple)
        return cache[obj_type]

    return func

#Some cached isinstance functions to reduce overhead
isinstance_template = cached_isinstance_generator((PropertyTemplate, ParameterTemplate, ConditionTemplate,
                                                   MaterialTemplate, ProcessTemplate, MeasurementTemplate))
isinstance_attribute_template = cached_isinstance_generator((PropertyTemplate, ParameterTemplate, ConditionTemplate))
isinstance_object_template = cached_isinstance_generator((MaterialTemplate, ProcessTemplate, MeasurementTemplate))
isinstance_spec = cached_isinstance_generator((MaterialSpec,ProcessSpec,IngredientSpec,MeasurementSpec))
isinstance_run = cached_isinstance_generator((MaterialRun,ProcessRun,IngredientRun,MeasurementRun))
isinstance_material_run = cached_isinstance_generator(MaterialRun)
isinstance_ingredient_run = cached_isinstance_generator(IngredientRun)
isinstance_link_by_uid = cached_isinstance_generator(LinkByUID)
isinstance_list_or_tuple = cached_isinstance_generator((list, tuple))
isinstance_dict_serializable = cached_isinstance_generator(DictSerializable)
