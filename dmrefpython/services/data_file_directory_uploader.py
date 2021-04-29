#imports
from data_file_io.data_file_directory import DataFileDirectory
from utilities.smwinservice import SMWinservice
from utilities.config_file_parser import ConfigFileParser
from utilities.argument_parsing import existing_dir, config_path, int_power_of_two
from utilities.logging import Logger
import pathlib, datetime

class DataFileDirectoryUploaderService(SMWinservice) :
    """
    Class to run uploading of a DataFileDirectory as a Windows service
    """

    #name, display name, and description for the service
    _svc_name_         = 'DataFileDirectoryUploader'
    _svc_display_name_ = 'Data File Directory Uploader'
    _svc_description_  = 'Chunks data files and produces them to a Kafka topic as they are added to a watched directory'
    #path to the config file taking the place of command line arguments for the service
    _config_file_path_ = pathlib.Path(__file__).parent / 'data_file_directory_uploader.config'

    #################### FUNCTIONS OVERLOADED FROM SMWinservice ####################

    def start(self) :
        """
        Called just before the service is requested to begin running; handles internal class setup and configuration
        """
        #make the logger
        filename = pathlib.Path(__file__).name.split('.')[0]
        self._logger = Logger(filename)
        #parse the configuration stuff in the file
        self._args = self._get_args()
        self._logger.add_file_handler(pathlib.Path(self._args.file_directory)/f'{filename}.log')
        #set up the DataFileDirectory
        self._upload_file_directory = DataFileDirectory(self._args.file_directory,logger=self._logger)
        #allow it to start uploading
        self._upload_file_directory.upload_running = True
        #set the start time
        self._start_time = datetime.datetime.now()

    def stop(self) :
        """
        Called just before the service is requested to stop running; handles externally stopping the uploading loop
        """
        #stop the loop in upload_files_as_added
        self._upload_file_directory.upload_running = False
        #set the stop time
        self._stop_time = datetime.datetime.now()

    def main(self) :
        """
        Called immediately after the service is started; calls upload_files_as_added to start the loop
        """
        if self._args.new_files_only :
            self._logger.info(f'Listening for files to be added to {self._args.file_directory}...')
        else :
            self._logger.info(f'Uploading files in/added to {self._args.file_directory}...')
        uploaded_filepaths = self._upload_file_directory.upload_files_as_added(self._args.config,self._args.topic_name,
                                                                               takes_user_input=False,
                                                                               n_threads=self._args.n_threads,
                                                                               chunk_size=self._args.chunk_size,
                                                                               max_queue_size=self._args.queue_max_size,
                                                                               update_secs=self._args.update_seconds,
                                                                               new_files_only=self._args.new_files_only)
        finish_time = datetime.datetime.now()
        self._logger.info(f'Done listening to {self._args.file_directory} for files to upload')
        final_msg = f'The following {len(uploaded_filepaths)} file'
        if len(uploaded_filepaths)==1 :
            final_msg+=' was'
        else :
            final_msg+='s were'
        final_msg+=f' uploaded between {run_start} and {run_stop}:\n'
        for fp in uploaded_filepaths :
            final_msg+=f'\t{fp}\n'
        self._logger.info(final_msg)

    #################### PRIVATE HELPER FUNCTIONS ####################

    #helper function to get the configs from the file and make sure they are all valid, and then return them in a namespace
    #basically cloning the command line argument parser from the command line script, but using the arguments from the config file
    def _get_args(self) :
        #parse the config file
        cfp = ConfigFileParser(self._config_file_path_,logger=self._logger)
        configs = cfp.get_config_dict_for_groups('data_file_directory_uploader')
        #add the config file path as an argument called "config"
        configs['config']=config_path(self._config_file_path_)
        #check the other arguments to make sure they're the correct type and replace them in the dictionary
        arg_checks = {'file_directory':existing_dir,
                      'topic_name':None, 
                      'n_threads':int,      
                      'chunk_size':int_power_of_two,
                      'queue_max_size':int,
                      'update_seconds':int,
                      'new_files_only':bool,
                     }
        for argname,argfunc in arg_checks.items() :
            if argname not in configs.keys() :
                self._logger.error(f'ERROR: missing argument {argname} in DataFileDirectoryUploaderService!',RuntimeError)
            try :
                configs[argname] = argfunc(configs[argname])
            except Exception as e :
                self._logger.error(f'ERROR: failed to parse argument {argname} in DataFileDirectoryUploaderService! Will re-reraise Exception.')
                raise (e)
        #return a Namespace with the populated arguments
        args = Namespace(file_directory=configs['file_directory'],
                         config=configs['config'],
                         topic_name=configs['topic_name'],
                         n_threads=configs['n_threads'],
                         chunk_size=configs['chunk_size'],
                         queue_max_size=configs['queue_max_size'],
                         update_seconds=configs['update_seconds'],
                         new_files_only=configs['new_files_only'],
                        )
        return args

if __name__ == '__main__' :
    DataFileDirectoryUploaderService.parse_command_line()
