#imports
import datetime, time
from threading import Lock
from ..utilities.misc import populated_kwargs
from ..shared.runnable import Runnable
from ..shared.controlled_process import ControlledProcessMultiThreaded
from ..my_kafka.consumer_group import ConsumerGroup
from .config import DATA_FILE_HANDLING_CONST, RUN_OPT_CONST
from .download_data_file import DownloadDataFileToDisk
from .data_file_directory import DataFileDirectory

class DataFileDownloadDirectory(DataFileDirectory,ControlledProcessMultiThreaded,ConsumerGroup,Runnable) :
    """
    Class representing a directory into which files are being reconstructed
    """

    #################### PROPERTIES ####################

    @property
    def other_datafile_kwargs(self) :
        return {} #Overload this in child classes to define additional keyword arguments 
                  #that should go to the specific datafile constructor
    @property
    def n_msgs_read(self) :
        return self.__n_msgs_read
    @property
    def completely_reconstructed_filepaths(self) :
        return self.__completely_reconstructed_filepaths
    @property
    def progress_msg(self) :
        progress_msg = 'The following files have been recognized so far:\n'
        for datafile in self.data_files_by_path.values() :
            progress_msg+=f'\t{datafile.full_filepath} (in progress)\n'
        for fp in self.completely_reconstructed_filepaths :
            progress_msg+=f'\t{fp} (completed)\n'
        return progress_msg

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,*args,datafile_type=DownloadDataFileToDisk,**kwargs) :
        """
        datafile_type = the type of datafile that the consumed messages should be assumed to represent
        In this class datafile_type should be something that extends DownloadDataFileToDisk
        """    
        kwargs = populated_kwargs(kwargs,{'n_consumers':kwargs.get('n_threads')})
        super().__init__(*args,**kwargs)
        if not issubclass(datafile_type,DownloadDataFileToDisk) :
            errmsg = 'ERROR: DataFileDownloadDirectory requires a datafile_type that is a subclass of '
            errmsg+= f'DownloadDataFileToDisk but {datafile_type} was given!'
            self.logger.error(errmsg,ValueError)
        self.__datafile_type = datafile_type
        self.__n_msgs_read = 0
        self.__completely_reconstructed_filepaths = []
        self.__thread_locks = {}

    def reconstruct(self) :
        """
        Consumes messages and writes their data to disk using several parallel threads to reconstruct the files 
        to which they correspond. Runs until the user inputs a command to shut it down. Returns the total number 
        of messages consumed, as well as the number of files whose reconstruction was completed during the run. 
        """
        msg = f'Will reconstruct files from messages in the {self.topic_name} topic using {self.n_threads} '
        msg+= f'thread{"s" if self.n_threads!=1 else ""}'
        self.logger.info(msg)
        lock = Lock()
        self.run([(lock,self.consumers[i]) for i in range(self.n_threads)])
        return self.__n_msgs_read, self.__completely_reconstructed_filepaths

    #################### PRIVATE HELPER FUNCTIONS ####################

    def _run_worker(self,lock,consumer) :
        """
        Consume messages expected to be DataFileChunks and try to write their data to disk in the directory, 
        paying attention to whether/how the files they're coming from end up fully reconstructed or mismatched 
        with their original hashes.
        Several iterations of this function run in parallel threads as part of a ControlledProcessMultiThreaded
        """
        #start the loop for while the controlled process is alive
        while self.alive :
            #consume a DataFileChunk message from the topic
            dfc = consumer.get_next_message(self.logger,0)
            if dfc is None :
                time.sleep(0.25) #wait just a bit to not over-tax things
                continue
            #set the chunk's rootdir to the working directory
            if dfc.rootdir is not None :
                errmsg = f'ERROR: message with key {dfc.message_key} has rootdir={dfc.rootdir} '
                errmsg+= '(should be None as it was just consumed)! Will ignore this message and continue.'
                self.logger.error(errmsg)
            dfc.rootdir = self.dirpath
            #add the chunk's data to the file that's being reconstructed
            with lock :
                self.__n_msgs_read+=1
                if dfc.filepath not in self.data_files_by_path.keys() :
                    self.data_files_by_path[dfc.filepath] = self.__datafile_type(dfc.filepath,
                                                                                 logger=self.logger,
                                                                                 **self.other_datafile_kwargs)
                    self.__thread_locks[dfc.filepath] = Lock()
            return_value = self.data_files_by_path[dfc.filepath].add_chunk(dfc,self.__thread_locks[dfc.filepath])
            if return_value in (DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS,
                                DATA_FILE_HANDLING_CONST.CHUNK_ALREADY_WRITTEN_CODE) :
                continue
            elif return_value==DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE :
                warnmsg = f'WARNING: hashes for file {self.data_files_by_path[dfc.filepath].filename} not matched '
                warnmsg+= 'after reconstruction! All data have been written to disk, but not as they were uploaded.'
                self.logger.warning(warnmsg)
                with lock :
                    del self.data_files_by_path[dfc.filepath]
                    del self.__thread_locks[dfc.filepath]
            elif return_value==DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE :
                msg = f'File {self.data_files_by_path[dfc.filepath].full_filepath.relative_to(dfc.rootdir)} '
                msg+= 'successfully reconstructed from stream'
                self.logger.info(msg)
                self.__completely_reconstructed_filepaths.append(dfc.filepath)
                with lock :
                    del self.data_files_by_path[dfc.filepath]
                    del self.__thread_locks[dfc.filepath]

    def _on_check(self) :
        msg = f'{self.__n_msgs_read} messages read, {len(self.__completely_reconstructed_filepaths)} files '
        msg+= 'completely reconstructed so far'
        self.logger.debug(msg)
        if len(self.data_files_by_path)>0 or len(self.__completely_reconstructed_filepaths)>0 :
            self.logger.debug(self.progress_msg)

    def _on_shutdown(self) :
        super()._on_shutdown()
        for consumer in self.consumers :
            consumer.close()

    #################### CLASS METHODS ####################

    @classmethod
    def get_command_line_arguments(cls) :
        args = ['output_dir','config','topic_name','update_seconds','consumer_group_ID']
        kwargs = {'n_threads':RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS}
        return args,kwargs

    @classmethod
    def run_from_command_line(cls,args=None) :
        """
        Run the download directory right from the command line
        """
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        #make the download directory
        reconstructor_directory = cls(args.output_dir,args.config,args.topic_name,
                                      n_threads=args.n_threads,
                                      consumer_group_ID=args.consumer_group_ID,
                                      update_secs=args.update_seconds,
                                     )
        #start the reconstructor running
        run_start = datetime.datetime.now()
        reconstructor_directory.logger.info(f'Listening for files to reconstruct in {args.output_dir}')
        n_msgs,complete_filenames = reconstructor_directory.reconstruct()
        run_stop = datetime.datetime.now()
        #shut down when that function returns
        reconstructor_directory.logger.info(f'File reconstructor writing to {args.output_dir} shut down')
        msg = f'{n_msgs} total messages were consumed'
        if len(complete_filenames)>0 :
            msg+=f' and the following {len(complete_filenames)} file'
            msg+=' was' if len(complete_filenames)==1 else 's were'
            msg+=' successfully reconstructed'
        msg+=f' from {run_start} to {run_stop}'
        for fn in complete_filenames :
            msg+=f'\n\t{fn}'
        reconstructor_directory.logger.info(msg)

#################### MAIN METHOD TO RUN FROM COMMAND LINE ####################

def main(args=None) :
    DataFileDownloadDirectory.run_from_command_line(args)

if __name__=='__main__' :
    main()
