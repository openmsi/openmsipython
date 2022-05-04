#imports
from threading import Lock
from dataclasses import dataclass
from atomicwrites import atomic_write
from ..utilities.misc import csv_header_line_from_dataclass
from ..shared.logging import LogOwner

@dataclass
class RegistryLine :
    filename : str
    filepath : str
    n_chunks : int
    chunks_delivered : str
    chunks_to_send : str

class ProducerFileRegistry(LogOwner) :
    """
    A class to manage an atomic csv file listing which portions 
    of which files have been uploaded to a particular topic

    dirpath    = path to the directory that should contain the csv file
    topic_name = the name of the topic that will be produced to (used in the filename)
    """

    def __init__(self,dirpath,topic_name,*args,**kwargs) :
        super().__init__(*args,**kwargs)
        self.__lock = Lock()
        self.__csv_filepath = dirpath/f'files_uploaded_to_{topic_name}.csv'
        if not self.__csv_filepath.isfile() :
            self.logger.info(f'Creating new producer file registry at {self.__csv_filepath}')
            self.__write_to_file(csv_header_line_from_dataclass(RegistryLine))
            self.__registry_lines_by_filepath = {}
        else :
            self.logger.info(f'Reading producer file registry at {self.__csv_filepath}')
            self.__registry_lines_by_filepath = self.__get_registry_lines_from_file()

    def __write_to_file(self,s,overwrite=True) :
        """
        atomically write a string to the csv file

        s = the string to write
        overwrite = whether an existing file of the same name should be overwritten
        """
        try :
            with self.__lock :
                with atomic_write(self.__csv_filepath,overwrite=overwrite) as fp :
                    fp.write(s)
        except Exception as e :
            errmsg = f'ERROR: failed to write to producer file registry at {self.__csv_filepath}! '
            errmsg+=  'Will reraise exception.'
            self.logger.error(errmsg,exc_obj=e)

    def __get_registry_lines_from_file(self) :
        """
        Return a dictionary of registry lines keyed by filepath read from the csv file
        """
        current_header_line = csv_header_line_from_dataclass(RegistryLine)
        field_names = ((current_header_line).split(','))[:-1]
        with open(self.__csv_filepath,'r') as fp :
            csv_lines = fp.readlines()
        if current_header_line!=csv_lines[0] :
            errmsg = f'ERROR: producer file registry at {self.__csv_filepath} has header line "{csv_lines[0]}" '
            errmsg+= f'which is incompatible with expected format "{current_header_line}"'
            self.logger.error(errmsg,RuntimeError)

