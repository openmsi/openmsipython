#imports
#from .attribute_templates import ATTR_TEMPL
#from .object_templates import OBJ_TEMPL
from .run_from_filemaker_record import MaterialRunFromFileMakerRecord

class LaserShockFlyerStack(MaterialRunFromFileMakerRecord) :
	"""
	A Flyer Stack created from a piece of glass, a foil, and an epoxy, cut using a Flyer Cutting program
	"""

	def __init__(self,record,specs,glass_IDs,foil_IDs,epoxy_IDs,flyer_cutting_programs) :
		pass
