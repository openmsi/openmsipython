#imports
import pathlib, traceback
from threading import Lock
from abc import ABC, abstractmethod
from ..utilities.misc import populated_kwargs
from ..utilities.logging import LogOwner
from ..utilities.controlled_process import ControlledProcessMultiThreaded
from ..my_kafka.consumer_group import ConsumerGroup
from .config import DATA_FILE_HANDLING_CONST
from .download_data_file import DownloadDataFileToMemory

class DataFileStreamProcessor(ControlledProcessMultiThreaded,LogOwner,ConsumerGroup,ABC) :
    """
    A class to consume DataFileChunk messages into memory and perform some operation(s) when entire files are available
    """

    #################### PROPERTIES ####################

    @property
    def other_datafile_kwargs(self) :
        return {} #Overload in child classes to add additional keyword arguments to the datafile constructor
    @property
    def n_msgs_read(self) :
        return self.__n_msgs_read
    @property
    def processed_filepaths(self) :
        return self.__processed_filepaths

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,*args,datafile_type=DownloadDataFileToMemory,**kwargs) :
        kwargs = populated_kwargs(kwargs,{'n_consumers':kwargs.get('n_threads')})
        super().__init__(*args,**kwargs)
        if not issubclass(datafile_type,DownloadDataFileToMemory) :
            errmsg = 'ERROR: DataFileStreamProcessor requires a datafile_type that is a subclass of '
            errmsg+= f'DownloadDataFileToMemory but {datafile_type} was given!'
            self.logger.error(errmsg,ValueError)
        self.__datafile_type = datafile_type
        self.__n_msgs_read = 0
        self.__processed_filepaths = []
        self.__download_files_by_filepath = {}
        self.__thread_locks_by_filepath = {}

    def process_files_as_read(self) :
        """
        Consumes messages and stores their data together separated by their original files.
        Uses several parallel threads to consume message and process fully read files. 
        Returns the total number of messages read and a list of the fully processed filenames.
        """
        msg = f'Will process files from messages in the {self.topic_name} topic using {self.n_threads} '
        msg+= f'thread{"s" if self.n_threads>1 else ""}'
        self.logger.info(msg)
        lock = Lock()
        self.run([(lock,self.consumers[i]) for i in range(self.n_threads)])
        return self.__n_msgs_read, self.__processed_filepaths

    #################### PRIVATE HELPER FUNCTIONS ####################

    @abstractmethod
    def _process_downloaded_data_file(self,datafile) :
        """
        Perform some operations on a given data file that has been fully read from the stream
        Returns None if processing was successful and an Exception otherwise
        Not implemented in the base class
        """
        pass

    def _on_check(self) :
        self.logger.debug(f'{self.__n_msgs_read} messages read, {len(self.__processed_filepaths)} files fully processed so far')

    def _run_worker(self,lock,consumer) :
        """
        Consume messages expected to be DataFileChunks and add their data to a file being reconstructed in memory, 
        paying attention to when each file has received all of its data and checking their contents against their original hashes.
        Several iterations of this function run in parallel threads as part of a ControlledProcessMultiThreaded
        """
        #start the loop for while the controlled process is alive
        while self.alive :
            #consume a message from the topic
            dfc = consumer.get_next_message(self.logger,0)
            if dfc is None :
                continue
            #set the chunk's rootdir to the current directory
            if dfc.rootdir is not None :
                self.logger.error(f'ERROR: message with key {dfc.message_key} has rootdir={dfc.rootdir} (should be None as it was just consumed)!',RuntimeError)
            dfc.rootdir = (pathlib.Path()).resolve()
            #add the chunk's data to the file that's being reconstructed
            with lock :
                if dfc.filepath not in self.__download_files_by_filepath.keys() :
                    self.__download_files_by_filepath[dfc.filepath] = self.__datafile_type(dfc.filepath,logger=self.logger,**self.other_datafile_kwargs)
                    self.__thread_locks_by_filepath[dfc.filepath] = Lock()
            return_value = self.__download_files_by_filepath[dfc.filepath].add_chunk(dfc,self.__thread_locks_by_filepath[dfc.filepath])
            #if the file hashes didn't match
            if return_value==DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE :
                self.logger.error(f'ERROR: file hashes for file {self.__download_files_by_filepath[dfc.filepath].filename} not matched after being fully read!',RuntimeError)
            #if the file has had all of its messages read successfully
            elif return_value==DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE :
                processing_retval = self._process_downloaded_data_file(self.__download_files_by_filepath[dfc.filepath])
                #if it was able to be processed
                if processing_retval is None :
                    self.logger.info(f'Fully-read file {self.__download_files_by_filepath[dfc.filepath].full_filepath.relative_to(dfc.rootdir)} successfully processed')
                    self.__processed_filepaths.append(dfc.filepath)
                #warn if it wasn't processed correctly
                else :
                    if isinstance(processing_retval,Exception) :
                        try :
                            raise processing_retval
                        except Exception as e :
                            self.logger.info(traceback.format_exc())
                    else :
                        self.logger.error(f'Return value from _process_downloaded_data_file = {processing_retval}')
                    warnmsg = f'WARNING: Fully-read file {self.__download_files_by_filepath[dfc.filepath].full_filepath.relative_to(dfc.rootdir)} '
                    warnmsg+= f'was not able to be processed. Check log lines above for more details on the specific error. '
                    warnmsg+= 'The messages for this file will need to be consumed again if the file is to be processed!'
                    self.logger.warning(warnmsg)
                with lock :
                    self.__n_msgs_read+=1                        
                    del self.__download_files_by_filepath[dfc.filepath]
                    del self.__thread_locks_by_filepath[dfc.filepath]
            #if the message was consumed and everything is moving along fine
            elif return_value in (DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS,DATA_FILE_HANDLING_CONST.CHUNK_ALREADY_WRITTEN_CODE) :
                with lock :
                    self.__n_msgs_read+=1
