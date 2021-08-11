#imports
from ..data_file_io.config import RUN_OPT_CONST
from ..data_file_io.data_file_upload_directory import DataFileUploadDirectory
from .config import LECROY_CONST
from .lecroy_data_file import UploadLecroyDataFile

class LecroyFileUploadDirectory(DataFileUploadDirectory) :
    """
    A class to select the relevant data from a Lecroy oscilloscope file 
    and upload it to a kafka topic as a group of messages
    """

    @property
    def other_datafile_kwargs(self) :
        return {'header_rows':self.__header_rows,
                'rows_to_skip':self.__rows_to_skip,
                'rows_to_select':self.__rows_to_select,
                'filename_append':LECROY_CONST.SKIMMED_FILENAME_APPEND,
                }

    def __init__(self,dirpath,
                 header_rows=LECROY_CONST.HEADER_ROWS,
                 rows_to_skip=LECROY_CONST.ROWS_TO_SKIP,
                 rows_to_select=LECROY_CONST.ROWS_TO_SELECT,
                 **kwargs) :
        """
        dirpath = path to the directory to watch
        header_rows = the number of rows in the raw files making up the header
        rows_to_skip = the number of rows in the raw files to completely ignore at the beginning
        rows_to_select = the number of rows to select in the raw files after the initial skip
        """
        self.__header_rows = header_rows
        self.__rows_to_skip = rows_to_skip
        self.__rows_to_select = rows_to_select
        super().__init__(dirpath,datafile_type=UploadLecroyDataFile,**kwargs)

    @classmethod
    def get_command_line_arguments(cls) :
        args = ['upload_dir','chunk_size','queue_max_size','update_seconds']
        kwargs = {'config':RUN_OPT_CONST.PRODUCTION_CONFIG_FILE,
                  'topic_name':LECROY_CONST.TOPIC_NAME,
                  'n_threads':1}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls,args=None) :
        """
        Function to run the upload directory right from the command line
        """
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        #make the LecroyFileUploadDirectory for the specified directory
        upload_file_directory = cls(args.upload_dir,update_secs=args.update_seconds)
        #listen for new files in the directory and run uploads as they come in until the process is shut down
        run_start = datetime.datetime.now()
        upload_file_directory.logger.info(f'Listening for Lecroy files to be added to {args.upload_dir}...')
        uploaded_filepaths = upload_file_directory.upload_files_as_added(args.config,args.topic_name,
                                                                         n_threads=args.n_threads,
                                                                         chunk_size=args.chunk_size,
                                                                         max_queue_size=args.queue_max_size,
                                                                         new_files_only=True)
        run_stop = datetime.datetime.now()
        upload_file_directory.logger.info(f'Done listening to {args.upload_dir} for Lecroy files to skim and upload')
        final_msg = f'The following {len(uploaded_filepaths)} file'
        if len(uploaded_filepaths)==1 :
            final_msg+=' was'
        else :
            final_msg+='s were'
        final_msg+=f' skimmed and uploaded between {run_start} and {run_stop}:\n'
        for fp in uploaded_filepaths :
            final_msg+=f'\t{fp}\n'
        upload_file_directory.logger.info(final_msg)

#################### MAIN METHOD TO RUN FROM COMMAND LINE ####################

def main(args=None) :
    LecroyFileUploadDirectory.run_from_command_line(args)

if __name__=='__main__' :
    main()
