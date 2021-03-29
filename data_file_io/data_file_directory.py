#imports
from .data_file import DataFile
from .utilities import produce_queue_of_file_chunks
from ..my_kafka.my_producers import TutorialClusterProducer
from ..utilities.misc import add_user_input, populated_kwargs
from ..utilities.logging import Logger
from ..utilities.config import RUN_OPT_CONST, TUTORIAL_CLUSTER_CONST
from confluent_kafka import Producer
from queue import Queue
from threading import Thread
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
        logger = the logger object to use (a new one will be created if none is supplied)
        """
        self._dirpath = dirpath
        self._logger = kwargs.get('logger')
        if self._logger is None :
            self._logger = Logger(os.path.basename(__file__).split('.')[0])
        self._filenames_done = set()
        for name in glob.glob(os.path.join(self._dirpath,'*')) :
            if os.path.isfile(name) :
                self._filenames_done.add(os.path.basename(name))

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
        #initialize variables for return values
        enqueued_filenames = []
        #initialize a thread to listen for and get user input and a queue to put it into
        user_input_queue = Queue()
        user_input_thread = Thread(target=add_user_input,args=(user_input_queue,))
        user_input_thread.daemon=True
        user_input_thread.start()
        #start the upload queue and thread
        self._logger.info(f'Will upload new files added to {self._dirpath} to the {kwargs["topic_name"]} topic using {kwargs["n_threads"]} threads')
        upload_queue = Queue()
        upload_thread = Thread(target=produce_queue_of_file_chunks,args=(upload_queue,kwargs['producer'],kwargs['topic_name'],kwargs['n_threads'],self._logger))
        upload_thread.start()
        #loop until the user inputs a command to stop
        last_update = time.time()
        while True:
            #print the "still alive" character at each given interval
            if time.time()-last_update>kwargs['update_seconds']:
                print('.')
                last_update = time.time()
            #if the user has put something in the console
            if not user_input_queue.empty():
                cmd = user_input_queue.get()
                #close the user input task and break out of the loop
                if cmd.lower() in ('q','quit') :
                    user_input_queue.task_done()
                    break
                #log progress so far
                elif cmd.lower() in ('c','check') :
                    progress_msg = f'The following {len(enqueued_filenames)} files have been enqueued so far:\n'
                    for ef in enqueued_filenames :
                        progress_msg+=f'{ef}\n'
                    self._logger.info(progress_msg)
            #check for new files in the directory
            new_filenames = [os.path.basename(fp) for fp in glob.glob(os.path.join(self._dirpath,'*')) 
                             if os.path.isfile(fp) and os.path.basename(fp) not in self._filenames_done]
            #add each new file's chunks to the Queue
            if len(new_filenames)>0 :
                for fn in new_filenames :
                    this_data_file = DataFile(os.path.join(self._dirpath,fn),logger=self._logger)
                    these_chunks = this_data_file.get_list_of_file_chunks(kwargs['chunk_size'])
                    for c in these_chunks :
                        upload_queue.put(c)
                    enqueued_filenames.append(fn)
                    self._filenames_done.add(fn)
            else :
                #wait for half the update time so we're not constantly checking for new files
                time.sleep(kwargs['update_seconds']/2.)
        #stop the uploading threads by adding "None" to the queue 
        upload_queue.put(None)
        #join the upload thread
        upload_thread.join()
        #return the list of enqueued filenames
        return enqueued_filenames
