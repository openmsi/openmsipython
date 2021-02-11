#imports
from ..oscilloscope.lecroy_file import LeCroyFile, LeCroyFileChunkInfo
from ..utilities.user_input import add_input
from ..utilities.logging import Logger
from ..config.oscilloscope import OSC_CONST
from queue import Queue
from threading import Thread, Lock
from multiprocessing import Manager
from argparse import ArgumentParser
import os, sys, time, datetime

# LeCroyFileReconstructor class
class LeCroyFileReconstructor() :
    """
    Class to consume messages and use them to reconstruct the LeCroy files to which they correspond
    """
    def __init__(self,logger_to_use=None) :
        if logger_to_use is None :
            logger_to_use = Logger()
        self._logger = logger_to_use
        manager = Manager()
        self._lecroy_file_dict = manager.dict()
        self._queue = Queue()
        self._threads = []

    #################### PUBLIC FUNCTIONS ####################

    def run(self,workingdir,n_threads,update_seconds) :
        """
        Consumes messages into a queue and processes them using several parallel threads to reconstruct 
        the files to which they correspond. Runs until the user inputs a command to shut it down.
        Returns the total number of messages consumed, as well as the number of files whose reconstruction 
        was completed during the run. 
        workingdir     = path to the directory that should hold the reconstructed files
        n_threads      = the number of threads to use for monitoring the Queue
        update_seconds = number of seconds to wait between printing a progress character to the console to indicate the program is alive
        """
        #initialize variables for return values
        self._n_msgs_read = 0
        self._n_files_completely_reconstructed = 0
        #initialize a queue to get user input and a thread to put to it
        input_queue = Queue()
        input_thread = Thread(target=add_input,args=(input_queue,))
        input_thread.daemon=True
        input_thread.start()
        #start up all of the threads that will get tokens from the main queue
        lock = Lock()
        for i in range(n_threads) :
            self._threads.append(Thread(target=self._add_items_from_queue_worker,args=(lock,workingdir)))
            self._threads[-1].start()
        #get the consumer and subscribe it to the lecroy_files topic
        consumer = OSC_CONST.CONSUMER
        consumer.subscribe([OSC_CONST.LECROY_FILE_TOPIC_NAME])
        #loop until the user inputs a command to stop
        last_update = time.time()
        while True:
            if time.time()-last_update>update_seconds:
                print('.')
                last_update = time.time()
            if not input_queue.empty():
                cmd = input_queue.get()
                if cmd.lower() in ('q','quit') :
                    input_queue.task_done()
                    break
                elif cmd.lower() in ('c','check') :
                    self._logger.info(f'{self._n_msgs_read} messages read, {self._n_files_completely_reconstructed} files completely reconstructed so far')
            consumed_msg = consumer.poll(0)
            if consumed_msg is not None :
                self._queue.put(consumed_msg.value())
        #join all the threads and return the number of messages read/files completely reconstructed
        for i in range(len(self._threads)) :
            self._queue.put(None)
        for t in self._threads :
            t.join()
        return self._n_msgs_read, self._n_files_completely_reconstructed

    #################### PRIVATE HELPER FUNCTIONS ####################

    #helper function to get items from a queue and add them to the lecroy files in the shared dictionary
    def _add_items_from_queue_worker(self,lock,workingdir) :
        #loop until None is pulled from the queue
        while True:
            token = self._queue.get()
            if token is None:
                break
            #get the file chunk info object from the token
            fci = LeCroyFileChunkInfo(token)
            #add the chunk's data to the file that's being reconstructed
            if fci.filename not in self._lecroy_file_dict.keys() :
                with lock :
                    self._lecroy_file_dict[fci.filename] = LeCroyFile(fci.filepath,self._logger)
            return_value = self._lecroy_file_dict[fci.filename].add_file_chunk(fci,workingdir)
            if return_value==OSC_CONST.FILE_HASH_MISMATCH_CODE :
                self._logger.error(f'ERROR: file hashes for file {fci.filename} not matched after reconstruction!',RuntimeError)
            elif return_value==OSC_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE :
                self._logger.info(f'File {fci.filename} successfully reconstructed locally from stream')
                with lock :
                    self._n_msgs_read+=1
                    self._n_files_completely_reconstructed+=1
                    del self._lecroy_file_dict[fci.filename]
            elif return_value==OSC_CONST.FILE_IN_PROGRESS :
                with lock :
                    self._n_msgs_read+=1
            #make sure the thread can be joined at any time
            self._queue.task_done()

#################### MAIN SCRIPT HELPER FUNCTIONS ####################

#make sure the command line arguments are valid
def check_args(args,logger) :
    #create the workingdir if it doesn't already exist
    if not os.path.isdir(args.workingdir) :
        os.mkdir(args.workingdir)

#################### MAIN SCRIPT ####################

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: path to directory to hold reconstructed files
    parser.add_argument('workingdir', help='Path to the directory to hold reconstructed files')
    #optional arguments
    parser.add_argument('--n_threads', default=10, type=int,
                        help='Maximum number of threads to use (default=10)')
    parser.add_argument('--update_seconds', default=10, type=int,
                        help='Number of seconds to wait between printing a "." to the console to indicate the program is alive (default=10)')
    args = parser.parse_args(args=args)
    #get the logger
    logger = Logger()
    #check the arguments
    check_args(args,logger)
    #make the LeCroyFileReconstructor to use
    file_reconstructor = LeCroyFileReconstructor(logger)
    #start the reconstructor running (returns total number of chunks read and total number of files completely reconstructed)
    run_start = datetime.datetime.now()
    n_msgs,n_complete_files = file_reconstructor.run(args.workingdir,args.n_threads,args.update_seconds)
    run_stop = datetime.datetime.now()
    #shut down when that function returns
    logger.info(f'File reconstructor writing to {args.workingdir} shut down')
    logger.info(f'{n_msgs} total messages were consumed and {n_complete_files} complete files were reconstructed from {run_start} to {run_stop}.')

if __name__=='__main__' :
    main()