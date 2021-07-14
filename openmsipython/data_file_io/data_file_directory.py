#imports
from .data_file_stream_reader import DataFileStreamReader
from .data_file import UploadDataFile, DownloadDataFile
from .utilities import produce_from_queue_of_file_chunks
from .config import RUN_OPT_CONST, DATA_FILE_HANDLING_CONST
from ..my_kafka.my_producers import MySerializingProducer
from ..my_kafka.my_consumers import MyDeserializingConsumer
from ..utilities.controlled_process import ControlledProcessSingleThread
from ..utilities.misc import add_user_input, populated_kwargs
from ..utilities.logging import Logger
from ..utilities.my_base_class import MyBaseClass
from queue import Queue, Empty
from threading import Thread, Lock
import pathlib, time

class DataFileDirectory(MyBaseClass) :
    """
    Base class representing any directory holding data files
    """

    #################### PROPERTIES ####################

    @property
    def dirpath(self) :
        return self.__dirpath
    @property
    def logger(self) :
        return self.__logger

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,dirpath,*args,**kwargs) :
        """
        dirpath = path to the directory 
        
        Possible keyword arguments:
        logger = the logger object to use (a new one will be created if none is supplied)
        """
        kwargs = populated_kwargs(kwargs,{'new_files_only':False})
        self.__dirpath = dirpath.resolve()
        self.__logger = kwargs.get('logger')
        if self.__logger is None :
            self.__logger = Logger(pathlib.Path(__file__).name.split('.')[0])
        self.data_files_by_path = {}
        super().__init__(*args,**kwargs)

class DataFileUploadDirectory(DataFileDirectory,ControlledProcessSingleThread) :
    """
    Class representing a directory being watched for new files to be added so they can be uploaded
    """

    #################### PROPERTIES ####################

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

    def upload_files_as_added(self,config_path,topic_name,**kwargs) :
        """
        Listen for new files to be added to the directory. Chunk and produce newly added files as messages to the topic.

        config_path = path to the config file to use in defining the producer
        topic_name  = name of the topic to produce messages to

        Possible keyword arguments:
        n_threads        = the number of threads to run at once during uploading
        chunk_size       = the size of each file chunk in bytes
        max_queue_size   = maximum number of items allowed to be placed in the upload queue at once
        new_files_only   = set to True if any files that already exist in the directory should be assumed to have been produced
                           i.e., if False (the default) then even files that are already in the directory will be enqueued to the producer
        """
        #set the important variables
        kwargs = populated_kwargs(kwargs,
                                  {'n_threads': RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                   'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                   'max_queue_size':RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE,
                                   'update_secs':RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS,
                                   'new_files_only':False,
                                  },self.logger)
        #start the producer 
        producer = MySerializingProducer.from_file(config_path,logger=self.logger)
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
        upload_queue = Queue(kwargs['max_queue_size'])
        upload_threads = []
        for ti in range(kwargs['n_threads']) :
            t = Thread(target=produce_from_queue_of_file_chunks,args=(upload_queue,
                                                                      producer,
                                                                      topic_name,
                                                                      self.logger))
            t.start()
            upload_threads.append(t)
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
            return
        #find the first file that's running and add some of its chunks to the upload queue 
        for datafile in self.data_files_by_path.values() :
            if datafile.upload_in_progress or datafile.waiting_to_upload :
                datafile.add_chunks_to_upload_queue(upload_queue,**kwargs)
                break

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
                    datafile.add_chunks_to_upload_queue(upload_queue,**kwargs)
                    break
        #stop the uploading threads by adding "None"s to their queues and joining them
        for ut in upload_threads :
            upload_queue.put(None)
        for ut in upload_threads :
            ut.join()
        self.logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
        producer.flush() #don't move on until all enqueued messages have been sent/received
        self.logger.info('Done!')

    def __find_new_files(self,to_upload=True) :
        """
        Search the directory for any unrecognized files and add them to _data_files_by_path

        to_upload = if False, new files found will NOT be marked for uploading (default is new files are expected to be uploaded)
        """
        #This is in a try/except in case a subdirectory is renamed while this method is running; it'll just return and try again
        try :
            for filepath in self.dirpath.rglob('*') :
                filepath = filepath.resolve()
                if self.filepath_should_be_uploaded(filepath) and (filepath not in self.data_files_by_path.keys()):
                    self.data_files_by_path[filepath]=UploadDataFile(filepath,to_upload=to_upload,rootdir=self.dirpath,logger=self.logger)
        except FileNotFoundError :
            return

class DataFileDownloadDirectory(DataFileDirectory,DataFileStreamReader) :
    """
    Class representing a directory into which files are being reconstructed
    """

    #################### PROPERTIES ####################

    @property
    def completely_reconstructed_filenames(self) :
        return self.__completely_reconstructed_filenames

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        self.__completely_reconstructed_filenames = set()
        self.__thread_locks_by_filepath = {}

    def reconstruct(self) :
        """
        Consumes messages into a queue and processes them using several parallel threads to reconstruct 
        the files to which they correspond. Runs until the user inputs a command to shut it down.
        Returns the total number of messages consumed, as well as the number of files whose reconstruction 
        was completed during the run. 
        """
        self.logger.info(f'Will reconstruct files from messages in the {self.topic_name} topic using {self.n_threads} threads')
        #start up all of the threads
        self._threads = []
        lock = Lock()
        for i in range(self.n_threads) :
            self._threads.append(Thread(target=self.__process_messages_worker,
                                        args=(lock)))
            self._threads[-1].start()
        #loop until the user inputs a command to stop
        last_update = time.time()
        while True:
            if kwargs['update_secs']!=-1 and time.time()-last_update>kwargs['update_secs']:
                self.logger.debug('.')
                last_update = time.time()
            if not self.user_input_queue.empty():
                cmd = self.user_input_queue.get()
                if cmd.lower() in ('q','quit') :
                    self.user_input_queue.task_done()
                    break
                elif cmd.lower() in ('c','check') :
                    self.logger.debug(f'{self.__n_msgs_read} messages read, {len(self.__completely_reconstructed_filenames)} files completely reconstructed so far')
        #stop the processes by adding "None" to the queues 
        for i in range(len(self._threads)) :
            self._queues[i].put(None)
        #join all the threads
        for t in self._threads :
            t.join()
        return self.__n_msgs_read, self.__completely_reconstructed_filenames

    #################### PRIVATE HELPER FUNCTIONS ####################

    def __process_messages_worker(self,lock) :
        """
        Read messages from a Queue as they are consumed and try to reconstruct them in the directory as DataFileChunks, 
        paying attention to whether/how the files they're coming from end up fully reconstructed or mismatched with their original hashes.
        Several iterations of this function are meant to run in parallel threads, speeding up the processing of the DataFileStreamReader Queue.
        """
        #start the infinite loop
        while True:
            #try to get something from the queue
            try :
                dfc = self._queues[list_index].get(block=False)
            #if there's nothing there, try to add a message consumed from the topic and then start over
            except Empty :
                try :
                    consumed_msg = consumer.poll(0)
                except Exception as e :
                    self.logger.warning(f'WARNING: encountered an error in a call to consumer.poll() and will skip the offending message. Error: {e}')
                    continue
                if consumed_msg is not None and consumed_msg.error() is None :
                    self._queues[list_index].put(consumed_msg.value())
                continue
            #if instead the queue had "None" in it then shut down the task
            if dfc is None:
                #make sure the thread can be joined
                self._queues[list_index].task_done()
                #close the consumer
                consumer.close()
                break
            #set the chunk's rootdir to the working directory
            if dfc.rootdir is not None :
                self.logger.error(f'ERROR: message with key {dfc.message_key} has rootdir={dfc.rootdir} (should be None as it was just consumed)!',RuntimeError)
            dfc.rootdir = self.dirpath
            #add the chunk's data to the file that's being reconstructed
            if dfc.filepath not in self.data_files_by_path.keys() :
                self.data_files_by_path[dfc.filepath] = DownloadDataFile(dfc.filepath,logger=self.logger)
                self.__thread_locks_by_filepath[dfc.filepath] = Lock()
            return_value = self.data_files_by_path[dfc.filepath].write_chunk_to_disk(dfc,self.__thread_locks_by_filepath[dfc.filepath])
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
