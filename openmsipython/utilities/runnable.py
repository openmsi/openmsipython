#imports
from abc import ABC, abstractmethod

class Runnable(ABC) :
	"""
	Class for any child classes that can be run on their own from the command line
	"""

	@classmethod
	@abstractmethod
	def run_from_command_line(cls,args=None) :
		pass #child classes should implement this function to do whatever it is they do when they run from the command line
