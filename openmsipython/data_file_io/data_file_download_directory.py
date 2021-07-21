#imports
import pathlib, datetime
from threading import Lock
from ..utilities.argument_parsing import MyArgumentParser
from ..utilities.controlled_process import ControlledProcessMultiThreaded
from ..utilities.runnable import Runnable
from ..utilities.misc import populated_kwargs
from ..utilities.logging import Logger
from ..my_kafka.consumer_group import ConsumerGroup
from .config import DATA_FILE_HANDLING_CONST
from .download_data_file import DownloadDataFileToDisk
from .data_file_directory import DataFileDirectory

class DataFileDownloadDirectory(DataFileDirectory,Runnable,ControlledProcessMultiThreaded,ConsumerGroup) :
    """
    Class representing a directory into which files are being reconstructed
    """

    #################### PROPERTIES ####################

    @property
    def n_msgs_read(self) :
        return self.__n_msgs_read
    @property
    def completely_reconstructed_filenames(self) :
        return self.__completely_reconstructed_filenames

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,*args,**kwargs) :
        kwargs = populated_kwargs(kwargs,{'n_consumers':kwargs.get('n_threads')})
        super().__init__(*args,**kwargs)
        self.__n_msgs_read = 0
        self.__completely_reconstructed_filenames = set()
        self.__thread_locks_by_filepath = {}

    def reconstruct(self) :
        """
        Consumes messages processes them using several parallel threads to reconstruct the files to which 
        they correspond. Runs until the user inputs a command to shut it down. Returns the total number of 
        messages consumed, as well as the number of files whose reconstruction was completed during the run. 
        """
        self.logger.info(f'Will reconstruct files from messages in the {self.topic_name} topic using {self.n_threads} thread{"s" if self.n_threads>1 else ""}')
        lock = Lock()
        self.run([(lock,self.consumers[i]) for i in range(self.n_threads)])
        return self.__n_msgs_read, self.__completely_reconstructed_filenames

    #################### PRIVATE HELPER FUNCTIONS ####################

    def _run_worker(self,lock,consumer) :
        """
        Consume messages expected to be DataFileChunks and try to write their data to disk in the directory, 
        paying attention to whether/how the files they're coming from end up fully reconstructed or mismatched with their original hashes.
        Several iterations of this function run in parallel threads as part of a ControlledProcessMultiThreaded
        """
        #start the loop for while the controlled process is alive
        while self.alive :
            #consume a DataFileChunk message from the topic
            dfc = consumer.get_next_message(0)
            if dfc is None :
                continue
            #set the chunk's rootdir to the working directory
            if dfc.rootdir is not None :
                self.logger.error(f'ERROR: message with key {dfc.message_key} has rootdir={dfc.rootdir} (should be None as it was just consumed)!',RuntimeError)
            dfc.rootdir = self.dirpath
            #add the chunk's data to the file that's being reconstructed
            if dfc.filepath not in self.data_files_by_path.keys() :
                self.data_files_by_path[dfc.filepath] = DownloadDataFileToDisk(dfc.filepath,logger=self.logger)
                self.__thread_locks_by_filepath[dfc.filepath] = Lock()
            return_value = self.data_files_by_path[dfc.filepath].add_chunk(dfc,self.__thread_locks_by_filepath[dfc.filepath])
            if return_value==DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE :
                self.logger.error(f'ERROR: file hashes for file {dfc.filename} not matched after reconstruction!',RuntimeError)
            elif return_value==DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE :
                self.logger.info(f'File {dfc.filepath.relative_to(dfc.rootdir)} successfully reconstructed locally from stream')
                with lock :
                    if dfc.filepath in self.data_files_by_path :
                        self.__n_msgs_read+=1
                        self.__completely_reconstructed_filenames.add(dfc.filepath)
                        del self.data_files_by_path[dfc.filepath]
                        del self.__thread_locks_by_filepath[dfc.filepath]
            elif return_value in (DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS,DATA_FILE_HANDLING_CONST.CHUNK_ALREADY_WRITTEN_CODE) :
                with lock :
                    self.__n_msgs_read+=1

    def _on_check(self) :
        self.logger.debug(f'{self.__n_msgs_read} messages read, {len(self.__completely_reconstructed_filenames)} files completely reconstructed so far')

    def _on_shutdown(self) :
        super()._on_shutdown()
        for consumer in self.consumers :
            consumer.close()

    #################### CLASS METHODS ####################

    @classmethod
    def run_from_command_line(cls,args=None) :
        """
        Run the download directory right from the command line
        """
        if args is None :
            #make the argument parser
            parser = MyArgumentParser('output_dir','config','topic_name','n_threads','update_seconds','consumer_group_ID')
        args = parser.parse_args(args=args)
        #get the logger
        filename = pathlib.Path(__file__).name.split('.')[0]
        logger = Logger(filename,filepath=pathlib.Path(args.output_dir)/f'{filename}.log')
        #make the download directory
        reconstructor_directory = cls(args.output_dir,args.config,args.topic_name,
                                      n_threads=args.n_threads,
                                      consumer_group_ID=args.consumer_group_ID,
                                      update_secs=args.update_seconds,
                                      logger=logger)
        #start the reconstructor running (returns total number of chunks read and total number of files completely reconstructed)
        run_start = datetime.datetime.now()
        logger.info(f'Listening for files to reconstruct in {args.output_dir}')
        n_msgs,complete_filenames = reconstructor_directory.reconstruct()
        run_stop = datetime.datetime.now()
        #shut down when that function returns
        logger.info(f'File reconstructor writing to {args.output_dir} shut down')
        msg = f'{n_msgs} total messages were consumed'
        if len(complete_filenames)>0 :
            msg+=f' and the following {len(complete_filenames)} file'
            msg+=' was' if len(complete_filenames)==1 else 's were'
            msg+=' successfully reconstructed'
        msg+=f' from {run_start} to {run_stop}'
        for fn in complete_filenames :
            msg+=f'\n\t{fn}'
        logger.info(msg)

#################### MAIN METHOD TO RUN FROM COMMAND LINE ####################

def main(args=None) :
    DataFileDownloadDirectory.run_from_command_line(args)

if __name__=='__main__' :
    main()
