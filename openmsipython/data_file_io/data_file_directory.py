#imports
from .data_file import DataFile
from .utilities import produce_from_queue_of_file_chunks
from .config import RUN_OPT_CONST, DATA_FILE_HANDLING_CONST
from ..my_kafka.my_producers import MySerializingProducer
from ..my_kafka.my_consumers import MyDeserializingConsumer
from ..utilities.misc import add_user_input, populated_kwargs
from ..utilities.logging import Logger
from queue import Queue, Empty
from threading import Thread, Lock
import pathlib, time, uuid

# DataFileDirectory Class
class DataFileDirectory() :
    """
    Class for representing a directory holding data files
    """

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,dirpath,**kwargs) :
        """
        dirpath = path to the directory 
        
        Possible keyword arguments:
        logger = the logger object to use (a new one will be created if none is supplied)
        """
        kwargs = populated_kwargs(kwargs,{'new_files_only':False})
        self._dirpath = dirpath
        self._logger = kwargs.get('logger')
        if self._logger is None :
            self._logger = Logger(pathlib.Path(__file__).name.split('.')[0])
        self._data_files_by_path = {}

    def upload_files_as_added(self,config_path,topic_name,**kwargs) :
        """
        Listen for new files to be added to the directory. Chunk and produce newly added files as messages to the topic.

        config_path = path to the config file to use in defining the producer
        topic_name  = name of the topic to produce messages to

        Possible keyword arguments:
        n_threads        = the number of threads to run at once during uploading
        chunk_size       = the size of each file chunk in bytes
        max_queue_size   = maximum number of items allowed to be placed in the upload queue at once
        update_secs      = number of seconds to wait between printing a progress character to the console to indicate the program is alive
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
                                  },self._logger)
        #start the producer 
        producer = MySerializingProducer.from_file(config_path,logger=self._logger)
        #if we're only going to upload new files, exclude what's already in the directory
        if kwargs['new_files_only'] :
            for filepath in self._dirpath.glob('*') :
                if self._filepath_should_be_uploaded(filepath) :
                    self._data_files_by_path[filepath]=DataFile(filepath,logger=self._logger,to_upload=False)
        #initialize a thread to listen for and get user input and a queue to put it into
        self.user_input_queue = Queue()
        user_input_thread = Thread(target=add_user_input,args=(self.user_input_queue,))
        user_input_thread.daemon=True
        user_input_thread.start()
        #start the upload queue and thread
        msg = 'Will upload '
        if kwargs['new_files_only'] :
            msg+='new files added to '
        else :
            msg+='files in '
        msg+=f'{self._dirpath} to the {topic_name} topic using {kwargs["n_threads"]} threads'
        self._logger.info(msg)
        upload_queue = Queue(kwargs['max_queue_size'])
        upload_threads = []
        for ti in range(kwargs['n_threads']) :
            t = Thread(target=produce_from_queue_of_file_chunks,args=(upload_queue,
                                                                      producer,
                                                                      topic_name,
                                                                      self._logger))
            t.start()
            upload_threads.append(t)
        #loop until the user inputs a command to stop
        last_update = time.time()
        while True:
            #print the "still alive" character at each given interval
            if kwargs['update_secs']!=-1 and time.time()-last_update>kwargs['update_secs']:
                self._logger.debug('.')
                last_update = time.time()
            #if the uploading has been stopped externally or the user has put something in the console
            if not self.user_input_queue.empty() :
                #make the progress message
                for filepath in self._dirpath.glob('*') :
                    if (filepath not in self._data_files_by_path.keys()) and self._filepath_should_be_uploaded(filepath) :
                        self._data_files_by_path[filepath]=DataFile(filepath,logger=self._logger)
                progress_msg = 'The following files have been recognized so far:\n'
                for datafile in self._data_files_by_path.values() :
                    if not datafile.to_upload :
                        continue
                    progress_msg+=f'\t{datafile.upload_status_msg}\n'
                cmd = self.user_input_queue.get()
                #close the user input task and break out of the loop
                if cmd.lower() in ('q','quit') :
                    self._logger.info('Will quit after all currently enqueued files are done being transferred.')
                    self._logger.info(progress_msg)
                    self.user_input_queue.task_done()
                    break
                #log progress so far
                elif cmd.lower() in ('c','check') :
                    self._logger.debug(progress_msg)
            #check for new files in the directory if we haven't already found some to run
            have_file = False
            for datafile in self._data_files_by_path.values() :
                if datafile.upload_in_progress or datafile.waiting_to_upload :
                    have_file=True
                    break
            if not have_file :
                for filepath in self._dirpath.glob('*') :
                    if self._filepath_should_be_uploaded(filepath) and (filepath not in self._data_files_by_path.keys()):
                        self._data_files_by_path[filepath]=DataFile(filepath,logger=self._logger)
                continue
            #find the first file that's running and add some of its chunks to the upload queue 
            for datafile in self._data_files_by_path.values() :
                if datafile.upload_in_progress or datafile.waiting_to_upload :
                    datafile.add_chunks_to_upload_queue(upload_queue,**kwargs)
                    break
        #add the remainder of any files currently in progress
        n_partially_done_files = len([df for df in self._data_files_by_path.values() if df.upload_in_progress])
        if n_partially_done_files>0 :
            partially_done_file_paths = [fp for fp,df in self._data_files_by_path.items() if df.upload_in_progress]
            msg='Will finish queueing the remainder of the following files before flushing the producer and quitting:\n'
            for pdfp in partially_done_file_paths :
                msg+=f'\t{pdfp}\n'
            self._logger.info(msg)
        while n_partially_done_files>0 :
            for datafile in self._data_files_by_path.values() :
                if datafile.upload_in_progress :
                    datafile.add_chunks_to_upload_queue(upload_queue,**kwargs)
                    break
            n_partially_done_files = len([df for df in self._data_files_by_path.values() if df.upload_in_progress])
        #stop the uploading threads by adding "None"s to their queues and joining them
        for ut in upload_threads :
            upload_queue.put(None)
        for ut in upload_threads :
            ut.join()
        self._logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
        producer.flush() #don't move on function until all enqueued messages have been sent/received
        self._logger.info('Done!')
        #return a list of filepaths that have been uploaded
        return [fp for fp,datafile in self._data_files_by_path.items() if datafile.fully_enqueued]

    def reconstruct(self,config_path,topic_name,**kwargs) :
        """
        Consumes messages into a queue and processes them using several parallel threads to reconstruct 
        the files to which they correspond. Runs until the user inputs a command to shut it down.
        Returns the total number of messages consumed, as well as the number of files whose reconstruction 
        was completed during the run. 

        config_path = path to the config file that should be used to define the consumer group
        topic_name  = name of the topic to consume messages from

        Possible keyword arguments:
        n_threads   = number of threads/consumers to use in listening for messages from the stream
        update_secs = number of seconds to wait between printing a progress character to the console to indicate the program is alive
        """
        kwargs = populated_kwargs(kwargs,
                                  {'n_threads':RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS,
                                   'update_secs':RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS,
                                   'consumer_group_id':str(uuid.uuid1()) #by default, make a new consumer group every time this code is run
                                  },self._logger)
        #initialize variables for return values
        self._n_msgs_read = 0
        self._completely_reconstructed_filenames = set()
        #initialize a thread to listen for and get user input and a queue to put it into
        self.user_input_queue = Queue()
        user_input_thread = Thread(target=add_user_input,args=(self.user_input_queue,))
        user_input_thread.daemon=True
        user_input_thread.start()
        self._logger.info(f'Will listen for files from the {topic_name} topic using {kwargs["n_threads"]} threads')
        #start up all of the queues and threads
        self._queues = []
        self._threads = []
        lock = Lock()
        for i in range(kwargs['n_threads']) :
            self._queues.append(Queue())
            self._threads.append(Thread(target=self._consume_and_process_messages_worker,
                                        args=(config_path,
                                              topic_name,
                                              kwargs['consumer_group_id'],
                                              lock,
                                              i)))
            self._threads[-1].start()
        #loop until the user inputs a command to stop
        last_update = time.time()
        while True:
            if kwargs['update_secs']!=-1 and time.time()-last_update>kwargs['update_secs']:
                self._logger.debug('.')
                last_update = time.time()
            if not self.user_input_queue.empty():
                cmd = self.user_input_queue.get()
                if cmd.lower() in ('q','quit') :
                    self.user_input_queue.task_done()
                    break
                elif cmd.lower() in ('c','check') :
                    self._logger.debug(f'{self._n_msgs_read} messages read, {len(self._completely_reconstructed_filenames)} files completely reconstructed so far')
        #stop the processes by adding "None" to the queues 
        for i in range(len(self._threads)) :
            self._queues[i].put(None)
        #join all the threads
        for t in self._threads :
            t.join()
        return self._n_msgs_read, self._completely_reconstructed_filenames

    #################### PRIVATE HELPER FUNCTIONS ####################

    #helper function to get DataFileChunks from a queue and write them to disk, paying attention to whether they've been fully reconstructed
    def _consume_and_process_messages_worker(self,config_path,topic_name,group_id,lock,list_index) :
        #start up the consumer
        consumer = MyDeserializingConsumer.from_file(config_path,logger=self._logger,group_id=group_id)
        consumer.subscribe([topic_name])
        #loop until None is pulled from the queue
        while True:
            try :
                dfc = self._queues[list_index].get(block=False)
            except Empty :
                try :
                    consumed_msg = consumer.poll(0)
                except Exception as e :
                    self._logger.warning(f'WARNING: encountered an error in a call to consumer.poll() and will skip the offending message. Error: {e}')
                if consumed_msg is not None and consumed_msg.error() is None :
                    self._queues[list_index].put(consumed_msg.value())
                continue
            if dfc is None:
                #make sure the thread can be joined
                self._queues[list_index].task_done()
                #close the consumer
                consumer.close()
                break
            #set the chunk's filepath to be in the working directory and add its data to the file that's being reconstructed
            if dfc.filepath is not None :
                self._logger.error(f'ERROR: message with key {dfc.message_key} has filepath={dfc.filepath} (should be None as it was just consumed)!',RuntimeError)
            dfc.filepath = self._dirpath/dfc.filename
            if dfc.filepath not in self._data_files_by_path.keys() :
                self._data_files_by_path[dfc.filepath] = (DataFile(dfc.filepath,logger=self._logger),Lock())
            return_value = self._data_files_by_path[dfc.filepath][0].write_chunk_to_disk(dfc,self._dirpath,self._data_files_by_path[dfc.filepath][1])
            if return_value==DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE :
                self._logger.error(f'ERROR: file hashes for file {dfc.filename} not matched after reconstruction!',RuntimeError)
            elif return_value==DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE :
                self._logger.info(f'File {dfc.filename} successfully reconstructed locally from stream')
                with lock :
                    if dfc.filepath in self._data_files_by_path :
                        self._n_msgs_read+=1
                        self._completely_reconstructed_filenames.add(dfc.filepath)
                        del self._data_files_by_path[dfc.filepath]
            elif return_value in (DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS,DATA_FILE_HANDLING_CONST.CHUNK_ALREADY_WRITTEN_CODE) :
                with lock :
                    self._n_msgs_read+=1

    #helper function to filter filepaths and return a boolean that's True if they should be uploaded
    def _filepath_should_be_uploaded(self,filepath) :
        if not isinstance(filepath,pathlib.PurePath) :
            self._logger.error(f'ERROR: {filepath} passed to _filepath_should_be_uploaded is not a Path!',TypeError)
        if filepath.name.startswith('.') :
            return False
        if filepath.name.endswith('.log') :
            return False
        return True

