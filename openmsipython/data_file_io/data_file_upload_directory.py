#imports
import pathlib, datetime, time
from threading import Thread
from queue import Queue
from ..utilities.misc import populated_kwargs
from ..shared.runnable import Runnable
from ..shared.controlled_process import ControlledProcessSingleThread
from ..my_kafka.my_producer import MyProducer
from .config import RUN_OPT_CONST
from .utilities import produce_from_queue_of_file_chunks
from .data_file_directory import DataFileDirectory
from .upload_data_file import UploadDataFile

class DataFileUploadDirectory(DataFileDirectory,ControlledProcessSingleThread,Runnable) :
    """
    Class representing a directory being watched for new files to be added so they can be uploaded
    """

    #################### PROPERTIES ####################

    @property
    def other_datafile_kwargs(self) :
        return {} # Overload this in subclasses to send extra keyword arguments to the individual datafile constructors
    @property
    def progress_msg(self) :
        self.__find_new_files()
        progress_msg = 'The following files have been recognized so far:\n'
        for datafile in self.data_files_by_path.values() :
            if not datafile.to_upload :
                continue
            progress_msg+=f'\t{datafile.upload_status_msg}\n'
        return progress_msg
    @property
    def have_file_to_upload(self) :
        for datafile in self.data_files_by_path.values() :
            if datafile.upload_in_progress or datafile.waiting_to_upload :
                return True
        return False
    @property
    def partially_done_file_paths(self) :
        return [fp for fp,df in self.data_files_by_path.items() if df.upload_in_progress]
    @property
    def n_partially_done_files(self) :
        return len(self.partially_done_file_paths)

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,dirpath,datafile_type=UploadDataFile,**kwargs) :
        super().__init__(dirpath,**kwargs)
        if not issubclass(datafile_type,UploadDataFile) :
            errmsg = 'ERROR: DataFileUploadDirectory requires a datafile_type that is a subclass of '
            errmsg+= f'UploadDataFile but {datafile_type} was given!'
            self.logger.error(errmsg,ValueError)
        self.__datafile_type = datafile_type
        

    def upload_files_as_added(self,config_path,topic_name,**kwargs) :
        """
        Listen for new files to be added to the directory. Chunk and produce newly added files as messages to the topic.

        config_path = path to the config file to use in defining the producer
        topic_name  = name of the topic to produce messages to

        Possible keyword arguments:
        n_threads        = the number of threads to use to produce from the shared queue
        chunk_size       = the size of each file chunk in bytes
        max_queue_size   = maximum number of items allowed to be placed in the upload queue at once
        new_files_only   = set to True if any files that already exist in the directory should be ignored
                           i.e., if False (the default) then even files that are already in the directory will be 
                           enqueued to the producer
        """
        #set the important variables
        kwargs = populated_kwargs(kwargs,
                                  {'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                   'max_queue_size':RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE,
                                   'new_files_only':False,
                                  },self.logger)
        self.__chunk_size = kwargs.get('chunk_size')
        #start the producer 
        self.__producer = MyProducer.from_file(config_path,logger=self.logger)
        #if we're only going to upload new files, exclude what's already in the directory
        if kwargs['new_files_only'] :
            self.__find_new_files(to_upload=False)
        #start the upload queue and thread
        msg = 'Will upload '
        if kwargs['new_files_only'] :
            msg+='new files added to '
        else :
            msg+='files in '
        msg+=f'{self.dirpath} to the {topic_name} topic using {kwargs["n_threads"]} threads'
        self.logger.info(msg)
        self.__upload_queue = Queue(kwargs['max_queue_size'])
        self.__upload_threads = []
        for ti in range(kwargs['n_threads']) :
            t = Thread(target=produce_from_queue_of_file_chunks,args=(self.__upload_queue,
                                                                      self.__producer,
                                                                      topic_name,
                                                                      self.logger))
            t.start()
            self.__upload_threads.append(t)
        #loop until the user inputs a command to stop
        self.run()
        #return a list of filepaths that have been uploaded
        return [fp for fp,datafile in self.data_files_by_path.items() if datafile.fully_enqueued]

    def filepath_should_be_uploaded(self,filepath) :
        """
        Filter filepaths from a glob and return a boolean that's True if they should be uploaded
        """
        if not isinstance(filepath,pathlib.PurePath) :
            self.logger.error(f'ERROR: {filepath} passed to filepath_should_be_uploaded is not a Path!',TypeError)
        if not filepath.is_file() :
            return False
        if filepath.name.startswith('.') :
            return False
        if filepath.name.endswith('.log') :
            return False
        return True

    #################### PRIVATE HELPER FUNCTIONS ####################

    def _run_iteration(self) :
        #check for new files in the directory if we haven't already found some to run
        if not self.have_file_to_upload :
            self.__find_new_files()
        #find the first file that's running and add some of its chunks to the upload queue 
        for datafile in self.data_files_by_path.values() :
            if datafile.upload_in_progress or datafile.waiting_to_upload :
                datafile.add_chunks_to_upload_queue(self.__upload_queue,
                                                    n_threads=len(self.__upload_threads),
                                                    chunk_size=self.__chunk_size)
                return

    def _on_check(self) :
        #log progress so far
        self.logger.debug(self.progress_msg)

    def _on_shutdown(self) :
        self.logger.info('Will quit after all currently enqueued files are done being transferred.')
        self.logger.info(self.progress_msg)
        #add the remainder of any files currently in progress
        if self.n_partially_done_files>0 :
            msg='Will finish queueing the remainder of the following files before flushing the producer and quitting:\n'
            for pdfp in self.partially_done_file_paths :
                msg+=f'\t{pdfp}\n'
            self.logger.info(msg)
        while self.n_partially_done_files>0 :
            for datafile in self.data_files_by_path.values() :
                if datafile.upload_in_progress :
                    datafile.add_chunks_to_upload_queue(self.__upload_queue,
                                                        n_threads=len(self.__upload_threads),
                                                        chunk_size=self.__chunk_size)
                    break
        #stop the uploading threads by adding "None"s to their queues and joining them
        for ut in self.__upload_threads :
            self.__upload_queue.put(None)
        for ut in self.__upload_threads :
            ut.join()
        self.logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
        self.__producer.flush() #don't move on until all enqueued messages have been sent/received

    def __find_new_files(self,to_upload=True) :
        """
        Search the directory for any unrecognized files and add them to _data_files_by_path

        to_upload = if False, new files found will NOT be marked for uploading 
                    (default is new files are expected to be uploaded)
        """
        #This is in a try/except in case a file is moved or a subdirectory is renamed while this method is running
        #it'll just return and try again if so
        try :
            time.sleep(0.25) # wait just a little bit here so that the watched directory isn't just constantly pinged
            for filepath in self.dirpath.rglob('*') :
                filepath = filepath.resolve()
                if self.filepath_should_be_uploaded(filepath) and (filepath not in self.data_files_by_path.keys()):
                    #wait until the file is actually available
                    file_ready = False
                    while not file_ready :
                        try :
                            fp = open(filepath)
                            fp.close()
                            file_ready = True
                        except PermissionError :
                            time.sleep(0.5)
                    self.data_files_by_path[filepath]=self.__datafile_type(filepath,
                                                                          to_upload=to_upload,
                                                                          rootdir=self.dirpath,
                                                                          logger=self.logger,
                                                                          **self.other_datafile_kwargs)
        except FileNotFoundError :
            return

    #################### CLASS METHODS ####################

    @classmethod
    def get_command_line_arguments(cls) :
        args = ['upload_dir','config','topic_name','chunk_size','queue_max_size','update_seconds','new_files_only']
        kwargs = {'n_threads':RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls,args=None) :
        """
        Function to run the upload directory right from the command line
        """
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        #make the DataFileDirectory for the specified directory
        upload_file_directory = cls(args.upload_dir,update_secs=args.update_seconds)
        #listen for new files in the directory and run uploads as they come in until the process is shut down
        run_start = datetime.datetime.now()
        if args.new_files_only :
            upload_file_directory.logger.info(f'Listening for files to be added to {args.upload_dir}...')
        else :
            upload_file_directory.logger.info(f'Uploading files in/added to {args.upload_dir}...')
        uploaded_filepaths = upload_file_directory.upload_files_as_added(args.config,args.topic_name,
                                                                         n_threads=args.n_threads,
                                                                         chunk_size=args.chunk_size,
                                                                         max_queue_size=args.queue_max_size,
                                                                         new_files_only=args.new_files_only)
        run_stop = datetime.datetime.now()
        upload_file_directory.logger.info(f'Done listening to {args.upload_dir} for files to upload')
        final_msg = f'The following {len(uploaded_filepaths)} file'
        if len(uploaded_filepaths)==1 :
            final_msg+=' was'
        else :
            final_msg+='s were'
        final_msg+=f' uploaded between {run_start} and {run_stop}:\n'
        for fp in uploaded_filepaths :
            final_msg+=f'\t{fp}\n'
        upload_file_directory.logger.info(final_msg)

#################### MAIN METHOD TO RUN FROM COMMAND LINE ####################

def main(args=None) :
    DataFileUploadDirectory.run_from_command_line(args)

if __name__=='__main__' :
    main()
