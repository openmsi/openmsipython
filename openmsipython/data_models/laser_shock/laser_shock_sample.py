#imports
from gemd.entity.util import make_instance
from gemd.entity.object.material_spec import MaterialSpec
from gemd.entity.object.process_spec import ProcessSpec
from gemd.entity.attribute.parameter import Parameter

class LaserShockSampleSpec(MaterialSpec) :
    """
    GEMD MaterialTemplate for a sample analyzed in the Laser Shock Lab
    """

    def __init__(self) :
        name = 'Laser Shock Sample'
        description = 'A sample received by the Laser Shock Lab'


#        Sample ID: 20-25
#        Material Processing: Metal
#        Supplier Name: Laszlo Kecskes (HEMI)
#        Supplier Product ID: 20-25
#        Bulk Wave  Speed: 
#        Density: 
#        Sample Name: 20-25 Mg-6Al 4Bc ECAE Billet
#        Purchase/Manufacture Date: 
#        Date: 09/15/2021
#        Performed By: DiMarco
#        Percentage 1: 94
#        Percentage 2: 6
#        Percentage 3: 0
#        Percentage 4: 0
#        Percentage 5: 0
#        Percentage 6: 0
#        Percentage 7: 0
#        Constituent 1: Mg
#        Constituent 2: Al
#        Constituent 3: N/A
#        Constituent 4: N/A
#        Constituent 5: N/A
#        Constituent 6: N/A
#        Constituent 7: N/A
#        Percentage Measure: Weight Percent
#        Processing Temperature: 300
#        Processing Route: 4Bc
#        General Notes: 
#        Grant Funding: MEDE Metals
#        Average Grain Size: 
#        Processing Geometry: Billet

class LaserShockSample :
    """
    An instance of the LaserShockSampleSpec
    """

    def __init__(self,filemaker_record) :
        self.__obj = make_instance(LaserShockSampleSpec)
