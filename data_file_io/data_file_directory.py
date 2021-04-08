#imports
from .data_file import DataFile
from .utilities import produce_from_queue_of_file_chunks
from ..my_kafka.my_producers import TutorialClusterProducer
from ..utilities.misc import add_user_input, populated_kwargs
from ..utilities.logging import Logger
from ..utilities.config import RUN_OPT_CONST, TUTORIAL_CLUSTER_CONST
from confluent_kafka import Producer
from queue import Queue
from threading import Thread, Lock
import os, glob, time

# DataFileDirectory Class
class DataFileDirectory() :
    """
    Class for representing a directory holding data files
    Can be used to listen for new files to be added and upload them as they are
    """
    def __init__(self,dirpath,**kwargs) :
        """
        dirpath = path to the directory to listen in on
        
        Possible keyword arguments:
        logger         = the logger object to use (a new one will be created if none is supplied)
        new_files_only = set to True if any files that already exist in the directory should be assumed to have been produced
                         i.e., if False (the default) then even files that are already in the directory will be enqueued to the producer
        """
        kwargs = populated_kwargs(kwargs,{'new_files_only':False})
        self._dirpath = dirpath
        self._logger = kwargs.get('logger')
        if self._logger is None :
            self._logger = Logger(os.path.basename(__file__).split('.')[0])
        self._data_files_by_path = {}
        if kwargs['new_files_only'] :
            for filepath in glob.glob(os.path.join(self._dirpath,'*')) :
                self._data_files_by_path[filepath]=DataFile(filepath,logger=self._logger,to_upload=False)

    #################### PUBLIC FUNCTIONS ####################

    def upload_files_as_added(self,**kwargs) :
        """
        Listen for new files to be added to the directory. Chunk and produce newly added files as messages to the topic.

        Possible keyword arguments:
        n_threads      = the number of threads to run at once during uploading
        chunk_size     = the size of each file chunk in bytes
        producer       = the producer object to use
        topic_name     = the name of the topic to use
        update_seconds = number of seconds to wait between printing a progress character to the console to indicate the program is alive
        """
        #set the important variables
        kwargs = populated_kwargs(kwargs,
                                  {'n_threads': RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS,
                                   'chunk_size': RUN_OPT_CONST.DEFAULT_CHUNK_SIZE,
                                   'producer': (TutorialClusterProducer(),Producer),
                                   'topic_name': TUTORIAL_CLUSTER_CONST.LECROY_FILE_TOPIC_NAME,
                                   'update_seconds':RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS,
                                  },self._logger)
        #initialize a thread to listen for and get user input and a queue to put it into
        user_input_queue = Queue()
        user_input_thread = Thread(target=add_user_input,args=(user_input_queue,))
        user_input_thread.daemon=True
        user_input_thread.start()
        #start the upload queue and thread
        msg = 'Will upload '
        if len(self._data_files_by_path)>0 :
            msg+='new files added to '
        else :
            msg+='files in'
        msg+=f'{self._dirpath} to the {kwargs["topic_name"]} topic using {kwargs["n_threads"]} threads'
        self._logger.info(msg)
        upload_queue = Queue()
        upload_threads = []
        lock = Lock()
        for ti in range(kwargs['n_threads']) :
            t = Thread(target=produce_from_queue_of_file_chunks,args=(upload_queue,
                                                                      kwargs['producer'],
                                                                      kwargs['topic_name'],
                                                                      self._logger,
                                                                      lock))
            t.start()
            upload_threads.append(t)
        #loop until the user inputs a command to stop
        last_update = time.time()
        while True:
            #print the "still alive" character at each given interval
            if time.time()-last_update>kwargs['update_seconds']:
                print('.')
                last_update = time.time()
            #if the user has put something in the console
            if not user_input_queue.empty() :
                cmd = user_input_queue.get()
                progress_msg = 'The following files have been recognized so far:\n'
                for datafile in self._data_files_by_path.values() :
                    if not datafile.to_upload :
                        continue
                    progress_msg+=f'\t{datafile.upload_status_msg}\n'
                #close the user input task and break out of the loop
                if cmd.lower() in ('q','quit') :
                    self._logger.info('Will quit after all currently enqueued files are done being transferred.')
                    self._logger.info(progress_msg)
                    user_input_queue.task_done()
                    break
                #log progress so far
                elif cmd.lower() in ('c','check') :
                    self._logger.info(progress_msg)
            #check for new files in the directory if we haven't already found some to run
            have_file = False
            for datafile in self._data_files_by_path.values() :
                if datafile.upload_in_progress :
                    have_file=True
                    break
            if not have_file :
                for filepath in glob.glob(os.path.join(self._dirpath,'*')) :
                    if filepath not in self._data_files_by_path.keys() :
                        self._data_files_by_path[filepath]=DataFile(filepath,logger=self._logger)
            #find the first file that's running and add some of its chunks to the upload queue 
            for datafile in self._data_files_by_path.values() :
                if datafile.upload_in_progress :
                    datafile.add_chunks_to_upload_queue(upload_queue,**kwargs)
                    break
        #stop the uploading threads by adding "None"s to their queues and joining them
        for ut in upload_threads :
            upload_queue.put(None)
        for ut in upload_threads :
            ut.join()
        self._logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
        kwargs['producer'].flush() #don't move on function until all enqueued messages have been sent/received
        self._logger.info('Done!')
        #return a list of filepaths that have been uploaded
        return [fp for fp,datafile in self._data_files_by_path.items() if datafile.fully_enqueued]
