#imports
from gemd.entity.template.property_template import PropertyTemplate
from gemd.entity.template.parameter_template import ParameterTemplate
from gemd.entity.bounds.categorical_bounds import CategoricalBounds

class MaterialProcessingTemplate(PropertyTemplate) :

    def __init__(self) :
        super().__init__(name='Material processing',
                         description='Possible values in the "Material Processing" menu buttons in the "Sample" layout',
                         bounds=CategoricalBounds(['Metal','Ceramic','Polymer','BMG','HEA','Composite'])
            )

class ProcessingGeometryTemplate(ParameterTemplate) :

    def __init__(self) :
        super().__init__(name='Processing geometry',
                         description='Possible values in the "Processing Geometry" menu buttons in the "Sample" layout',
                         bounds=CategoricalBounds(['Billet','Plate'])
            )

class ProcessingRouteTemplate(ParameterTemplate) :

    def __init__(self) :
        super().__init__(name='Processing route',
                         description='Possible values in the "Processing Route" menu buttons in the "Sample" layout',
                         bounds=CategoricalBounds(['4Bc'])
            )
