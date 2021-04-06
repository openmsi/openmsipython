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
        self._filenames_done = set()
        if kwargs['new_files_only'] :
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
        chunks_to_upload_by_filename = {}
        #initialize a thread to listen for and get user input and a queue to put it into
        user_input_queue = Queue()
        user_input_thread = Thread(target=add_user_input,args=(user_input_queue,))
        user_input_thread.daemon=True
        user_input_thread.start()
        #start the upload queue and thread
        self._logger.info(f'Will upload new files added to {self._dirpath} to the {kwargs["topic_name"]} topic using {kwargs["n_threads"]} threads')
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
            if not user_input_queue.empty():
                cmd = user_input_queue.get()
                #close the user input task and break out of the loop
                if cmd.lower() in ('q','quit') :
                    user_input_queue.task_done()
                    break
                #log progress so far
                elif cmd.lower() in ('c','check') :
                    progress_msg = f'The following {len(chunks_to_upload_by_filename.keys())} files have been recognized so far:\n'
                    for fn,chunk_list in chunks_to_upload_by_filename.items() :
                        progress_msg+=f'\t{fn}'
                        if len(chunk_list)==1 and chunk_list[0]=='done' :
                            progress_msg+=' (fully enqueued)'
                        elif len(chunk_list)==0 :
                            progress_msg+=' (waiting to enqueue)'
                        else :
                            progress_msg+=' (in progress)'
                        progress_msg+='\n'
                    self._logger.info(progress_msg)
            #check for new files in the directory if we haven't already found some to run
            have_file = False
            if len(chunks_to_upload_by_filename.keys())>0 :
                for chunk_list in chunks_to_upload_by_filename.values() :
                    if len(chunk_list)==0 :
                        have_file=True
            if not have_file :
                new_filenames = [os.path.basename(fp) for fp in glob.glob(os.path.join(self._dirpath,'*')) 
                                 if os.path.isfile(fp) and os.path.basename(fp) not in self._filenames_done
                                 and os.path.basename(fp) not in chunks_to_upload_by_filename.keys()]
                for fn in new_filenames :
                    chunks_to_upload_by_filename[fn]=[]
            #find a file to enqueue and get its list of chunks 
            for fn,cl in chunks_to_upload_by_filename.items() :
                if len(cl)==0 :
                    this_data_file = DataFile(os.path.join(self._dirpath,fn),logger=self._logger)
                    these_chunks = this_data_file.get_list_of_file_chunks(kwargs['chunk_size'])
                    chunks_to_upload_by_filename[fn]=these_chunks
                    break
            #pop some chunks from any file in progress and enqueue them
            for fn,cl in chunks_to_upload_by_filename.items() :
                if len(cl)==1 and cl[0]=='done' :
                    continue
                ic=0
                while len(cl)>1 and ic in range(kwargs['n_threads']) :
                    upload_queue.put(cl.pop(0))
                    ic+=1
                if len(cl)==1 :
                    upload_queue.put(cl.pop(0))
                    cl.append('done')
                    self._filenames_done.add(fn)
                    continue
                else :
                    break
        #stop the uploading threads by adding "None"s to the queue and joining the threads
        for ut in upload_threads :
            upload_queue.put(None)
        for ut in upload_threads :
            ut.join()
        self._logger.info('Waiting for all enqueued messages to be delivered (this may take a moment)....')
        kwargs['producer'].flush() #don't leave the function until all messages have been sent/received
        self._logger.info('Done!')
        #return a list of filenames that have finished being enqueued
        enqueued_filenames = []
        for fn,cl in chunks_to_upload_by_filename.items() :
            if len(cl)==1 and cl[0]=='done' :
                enqueued_filenames.append(fn)
        return enqueued_filenames
