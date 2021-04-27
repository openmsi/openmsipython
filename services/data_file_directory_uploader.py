#imports
from ..utilities.smwinservice import SMWinservice
from ..data_file_io.data_file_directory import DataFileDirectory
import pathlib

class DataFileDirectoryUploaderService(SMWinservice) :

    #name, display name, and description for the service
    _svc_name_         = 'DataFileDirectoryUploader'
    _svc_display_name_ = 'Data File Directory Uploader'
    _svc_description_  = 'Chunks data files and produces them to a Kafka topic as they are added to a watched directory'
    #path to the config file taking the place of command line arguments for the service
    _config_file_path_ = pathlib.Path(__file__).parent / 'data_file_directory_uploader.config'

    def start(self) :
    """
    Called just before the service is requested to begin running; handles internal class setup and configuration
    """
        self.isrunning=True

    def stop(self) :
        self.isrunning=False

    def main(self) :
        pass

if __name__ == '__main__' :
    DataFileDirectoryUploaderService.parse_command_line()
