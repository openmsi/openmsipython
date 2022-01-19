#imports
import pathlib, traceback
from abc import ABC, abstractmethod
from ..shared.logging import LogOwner
from .config import DATA_FILE_HANDLING_CONST
from .download_data_file import DownloadDataFileToMemory
from .data_file_chunk_processor import DataFileChunkProcessor

class DataFileStreamProcessor(DataFileChunkProcessor,LogOwner,ABC) :
    """
    A class to consume DataFileChunk messages into memory and perform some operation(s) when entire files are available
    """

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self,*args,datafile_type=DownloadDataFileToMemory,**kwargs) :
        """
        datafile_type = the type of datafile that the consumed messages should be assumed to represent
        In this class datafile_type should be something that extends DownloadDataFileToMemory
        """   
        super().__init__(*args,datafile_type=datafile_type,**kwargs)
        if not issubclass(datafile_type,DownloadDataFileToMemory) :
            errmsg = 'ERROR: DataFileStreamProcessor requires a datafile_type that is a subclass of '
            errmsg+= f'DownloadDataFileToMemory but {datafile_type} was given!'
            self.logger.error(errmsg,ValueError)

    def process_files_as_read(self) :
        """
        Consumes messages and stores their data together separated by their original files.
        Uses several parallel threads to consume message and process fully read files. 
        Returns the total number of messages read and a list of the fully processed filenames.
        """
        msg = f'Will process files from messages in the {self.topic_name} topic using {self.n_threads} '
        msg+= f'thread{"s" if self.n_threads>1 else ""}'
        self.logger.info(msg)
        self.run()
        return self.n_msgs_read, self.n_msgs_processed, self.completely_processed_filepaths

    #################### PRIVATE HELPER FUNCTIONS ####################

    @abstractmethod
    def _process_downloaded_data_file(self,datafile,lock) :
        """
        Perform some operations on a given data file that has been fully read from the stream
        Can optionally lock other threads using the given lock
        Returns None if processing was successful and an Exception otherwise
        Not implemented in the base class
        """
        pass

    def _process_message(self,lock,dfc):
        retval = super()._process_message(lock, dfc, (pathlib.Path()).resolve(), self.logger)
        if retval==True :
            return retval
        #if the file has had all of its messages read successfully, send it to the processing function
        if retval==DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE :
            short_filepath = self.files_in_progress_by_path[dfc.filepath].full_filepath.relative_to(dfc.rootdir)
            msg = f'Processing {short_filepath}...'
            self.logger.info(msg)
            processing_retval = self._process_downloaded_data_file(self.files_in_progress_by_path[dfc.filepath],lock)
            with lock :
                del self.files_in_progress_by_path[dfc.filepath]
                del self.locks_by_fp[dfc.filepath]
            #if it was able to be processed
            if processing_retval is None :
                self.logger.info(f'Fully-read file {short_filepath} successfully processed')
                self.completely_processed_filepaths.append(dfc.filepath)
                return True
            #warn if it wasn't processed correctly
            else :
                if isinstance(processing_retval,Exception) :
                    try :
                        raise processing_retval
                    except Exception :
                        self.logger.info(traceback.format_exc())
                else :
                    self.logger.error(f'Return value from _process_downloaded_data_file = {processing_retval}')
                warnmsg = f'WARNING: Fully-read file {short_filepath} was not able to be processed. '
                warnmsg+= 'Check log lines above for more details on the specific error. '
                warnmsg+= 'The messages for this file will need to be consumed again if the file is to be processed!'
                self.logger.warning(warnmsg)
                return False
        #if the file hashes didn't match, return False
        elif retval==DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE :
            warnmsg = f'WARNING: file hashes for file {self.files_in_progress_by_path[dfc.filepath].filename} '
            warnmsg+= 'not matched after being fully read! This file will not be processed.'
            self.logger.warning(warnmsg)
            with lock :
                del self.files_in_progress_by_path[dfc.filepath]
                del self.locks_by_fp[dfc.filepath]
            return False
        else :
            self.logger.error(f'ERROR: unrecognized add_chunk return code ({retval})!',NotImplementedError)
            return False

    def _on_check(self) :
        msg = f'{self.n_msgs_read} messages read, {self.n_msgs_processed} messages processed, '
        msg+= f'{len(self.completely_processed_filepaths)} files completely reconstructed so far'
        self.logger.debug(msg)
        if len(self.files_in_progress_by_path)>0 or len(self.completely_processed_filepaths)>0 :
            self.logger.debug(self.progress_msg)
