#imports
from ..utilities.smwinservice import SMWinservice

class DataFileDirectoryUploaderService(SMWinservice) :

	_svc_name_ = 'DataFileDirectoryUploader'
	_svc_display_name_ = 'Data File Directory Uploader'
	_svc_description_ = 'Chunks data files and produces them to a Kafka topic as they are added to a watched directory'

	def start(self) :
		self.isrunning = True

	def stop(self) :
		self.isrunning=False

	def main(self) :
		pass

if __name__ == '__main__' :
	DataFileDirectoryUploaderService.parse_command_line()