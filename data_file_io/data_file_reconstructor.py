#imports
from .data_file import DataFile
from .data_file_chunk import DataFileChunk
from ..my_kafka.my_consumers import TutorialClusterConsumer
from ..utilities.misc import add_user_input, populated_kwargs
from ..utilities.logging import Logger
from ..utilities.config import RUN_OPT_CONST, TUTORIAL_CLUSTER_CONST, DATA_FILE_HANDLING_CONST
from confluent_kafka import Consumer
from queue import Queue
from threading import Thread, Lock
import os, time, uuid

# DataFileReconstructor class
class DataFileReconstructor() :
    """
    Class to consume packed DataFileChunk messages and use them to reconstruct the complete files to which they correspond
    """
    def __init__(self,**kwargs) :
        """
        Possible keyword arguments:
        logger = the logger object to use (a new one will be created if none is supplied)
        """
        self._logger = kwargs.get('logger')
        if self._logger is None :
            self._logger = Logger(os.path.basename(__file__).split('.')[0])
        self._data_files_by_name = {}
        self._threads = []
        self._consumers = []
        self._queues = []

    #################### PUBLIC FUNCTIONS ####################

    def run(self,workingdir,**kwargs) :
        """
        Consumes messages into a queue and processes them using several parallel threads to reconstruct 
        the files to which they correspond. Runs until the user inputs a command to shut it down.
        Returns the total number of messages consumed, as well as the number of files whose reconstruction 
        was completed during the run. 

        workingdir = path to the directory that should hold the reconstructed files

        Possible keyword arguments:
        n_threads         = number of threads/consumers to use in listening for messages from the stream (default will use # of partitions+1)
        update_seconds    = number of seconds to wait between printing a progress character to the console to indicate the program is alive
        consumer_type     = type of consumer that the threads will use
        topic_name        = name of the topic to which the consumers should be subscribed
        consumer_group_id = id to be shared by each of the consumers that will be spawned
        """
        kwargs = populated_kwargs(kwargs,
                                 {'n_threads':RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS,
                                 'update_seconds':RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS,
                                 'consumer_type':(TutorialClusterConsumer,Consumer),
                                 'topic_name':TUTORIAL_CLUSTER_CONST.LECROY_FILE_TOPIC_NAME,
                                 'consumer_group_id':str(uuid.uuid1()) #by default, make a new consumer group every time this code is run
                                 },self._logger)
        #initialize variables for return values
        self._n_msgs_read = 0
        self._completely_reconstructed_filenames = set()
        #initialize a thread to listen for and get user input and a queue to put it into
        user_input_queue = Queue()
        user_input_thread = Thread(target=add_user_input,args=(user_input_queue,))
        user_input_thread.daemon=True
        user_input_thread.start()
        self._logger.info(f'Will listen for files from the {kwargs["topic_name"]} topic using {kwargs["n_threads"]} threads')
        #start up all of the queues, consumers, and threads
        lock = Lock()
        for i in range(kwargs['n_threads']) :
            self._queues.append(Queue())
            self._consumers.append((kwargs['consumer_type'])(group_id=kwargs['consumer_group_id']))
            self._consumers[-1].subscribe([kwargs['topic_name']])
            self._threads.append(Thread(target=self._add_items_from_queues_worker,args=(lock,workingdir,i)))
            self._threads[-1].start()
        #loop until the user inputs a command to stop
        last_update = time.time()
        while True:
            if time.time()-last_update>kwargs['update_seconds']:
                print('.')
                last_update = time.time()
            if not user_input_queue.empty():
                cmd = user_input_queue.get()
                if cmd.lower() in ('q','quit') :
                    user_input_queue.task_done()
                    break
                elif cmd.lower() in ('c','check') :
                    self._logger.info(f'{self._n_msgs_read} messages read, {len(self._completely_reconstructed_filenames)} files completely reconstructed so far')
            for i in range(len(self._threads)) :
                consumed_msg = self._consumers[i].poll(0)
                if consumed_msg is not None and consumed_msg.error() is None :
                    self._queues[i].put(consumed_msg.value())
        #stop the processes by adding "None" to the queues 
        for i in range(len(self._threads)) :
            self._queues[i].put(None)
        #join all the threads
        for t in self._threads :
            t.join()
        #close all the consumers
        for consumer in self._consumers :
            consumer.close()
        return self._n_msgs_read, self._completely_reconstructed_filenames

    #################### PRIVATE HELPER FUNCTIONS ####################

    #helper function to get items from a queue and add them to the lecroy files in the shared dictionary
    def _add_items_from_queues_worker(self,lock,workingdir,list_index) :
        #loop until None is pulled from the queue
        while True:
            token = self._queues[list_index].get()
            if token is None:
                #make sure the thread can be joined
                self._queues[list_index].task_done()
                break
            #get the file chunk object from the token
            dfc = DataFileChunk.from_token(token,logger=self._logger)
            #add the chunk's data to the file that's being reconstructed
            if dfc.filename not in self._data_files_by_name.keys() :
                with lock :
                    self._data_files_by_name[dfc.filename] = (DataFile(dfc.filepath,logger=self._logger),Lock())
            return_value = self._data_files_by_name[dfc.filename][0].write_chunk_to_disk(dfc,workingdir,self._data_files_by_name[dfc.filename][1])
            if return_value==DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE :
                with lock :
                    self._logger.error(f'ERROR: file hashes for file {dfc.filename} not matched after reconstruction!',RuntimeError)
            elif return_value==DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE :
                with lock :
                    self._logger.info(f'File {dfc.filename} successfully reconstructed locally from stream')
                with lock :
                    if dfc.filename in self._data_files_by_name :
                        self._n_msgs_read+=1
                        self._completely_reconstructed_filenames.add(dfc.filename)
                        del self._data_files_by_name[dfc.filename]
            elif return_value==DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS :
                with lock :
                    self._n_msgs_read+=1
