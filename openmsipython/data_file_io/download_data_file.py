#imports
from .data_file import DataFile
from abc import ABC, abstractmethod
from contextlib import nullcontext
from .config import DATA_FILE_HANDLING_CONST
from hashlib import sha512
import os

class DownloadDataFile(DataFile,ABC) :
    """
    Class to represent a data file that will be read as messages from a topic
    """

    @property
    @abstractmethod
    def check_file_hash(self) :
        pass #the hash of the data in the file after it was read; not implemented in the base class

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        #start an empty set of this file's downloaded offsets
        self._chunk_offsets_downloaded = set()
        #a thread lock to guarantee that only one thread does certain critical things to the file at once

    def add_chunk(self,dfc,thread_lock=nullcontext(),*args,**kwargs) :
        """
        A function to process a chunk that's been read from a topic
        Returns a number of codes based on what effect adding the chunk had
        
        This function calls _on_add_chunk, 
        
        dfc = the DataFileChunk object whose data should be added
        thread_lock = the lock object to acquire/release so that race conditions don't affect 
                      reconstruction of the files (optional, only needed if running this function asynchronously)
        """
        #the filepath of this DownloadDataFile and of the given DataFileChunk must match
        if dfc.filepath!=self.filepath :
            self.logger.error(f'ERROR: filepath mismatch between data file chunk {dfc._filepath} and data file {self.filepath}',ValueError)
        #if this chunk's offset has already been written to disk, return the "already written" code
        if dfc.chunk_offset_write in self._chunk_offsets_downloaded :
            return DATA_FILE_HANDLING_CONST.CHUNK_ALREADY_WRITTEN_CODE
        #acquire the thread lock to make sure this process is the only one dealing with this particular file
        with thread_lock:
            #call the function to actually add the chunk
            self._on_add_chunk(dfc,*args,**kwargs)
            #add the offset of the added chunk to the set of reconstructed file chunks
            self._chunk_offsets_downloaded.add(dfc.chunk_offset_write)
            #if this chunk was the last that needed to be added, check the hashes to make sure the file is the same as it was originally
            if len(self._chunk_offsets_downloaded)==dfc.n_total_chunks :
                if self.check_file_hash!=dfc.file_hash :
                    return DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE
                else :
                    return DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE
            else :
                return DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS

    @abstractmethod
    def _on_add_chunk(dfc,*args,**kwargs) :
        """
        A function to actually process a new chunk being added to the file
        This function is executed while a thread lock is acquired so it will never run asynchronously
        Also any DataFileChunks passed to this function are guaranteed to have unique offsets
        Not implemented in the base class
        """
        pass

class DownloadDataFileToDisk(DownloadDataFile) :
    """
    Class to represent a data file that will be reconstructed on disk using messages read from a topic
    """

    @property
    def check_file_hash(self) :
        check_file_hash = sha512()
        with open(self.filepath,'rb') as fp :
            data = fp.read()
        check_file_hash.update(data)
        return check_file_hash.digest()

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        #create the parent directory of the file if it doesn't exist yet (in case the file is in a new subdirectory)
        if not self.filepath.parent.is_dir() :
            self.filepath.parent.mkdir(parents=True)

    def _on_add_chunk(self,dfc) :
        """
        Add the data from a given file chunk to this file on disk
        """
        mode = 'r+b' if self.filepath.is_file() else 'w+b'
        with open(self.filepath,mode) as fp :
            fp.seek(dfc.chunk_offset_write)
            fp.write(dfc.data)
            fp.flush()
            os.fsync(fp.fileno())
            fp.close()

class DownloadDataFileToMemory(DownloadDataFile) :
    """
    Class to represent a data file that will be held in memory and populated by the contents of messages from a topic
    """

    @property
    def bytestring(self) :
        if self.__bytestring is None :
            self.__create_bytestring()
        return self.__bytestring
    @property
    def check_file_hash(self) :
        check_file_hash = sha512()
        check_file_hash.update(self.bytestring)
        return check_file_hash.digest()

    def __init__(self,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        #start a dictionary of the file data by their offsets
        self.__chunk_data_by_offset = {}
        #placeholder for the eventual full data bytestring
        self.__bytestring = None

    def _on_add_chunk(self,dfc) :
        """
        Add the data from a given file chunk to the dictionary of data by offset
        """
        self.__chunk_data_by_offset[dfc.chunk_offset_write] = dfc.data

    def __create_bytestring(self) :
        """
        Makes all of the data held in the dictionary into a single bytestring ordered by offset of each chunk
        """
        bytestring = b''
        for data in [self.__chunk_data_by_offset[offset] for offset in sorted(self.__chunk_data_by_offset.keys())] :
            bytestring+=data
        self.__bytestring = bytestring
