#imports
from .lecroy_data_file import UploadLecroyDataFile
from .config import LECROY_CONST
from ..data_file_io.data_file_directory import DataFileUploadDirectory

class LecroyFileUploadDirectory(DataFileUploadDirectory) :
    """
    A class to select the relevant data from a Lecroy oscilloscope file and upload it to a kafka topic as a group of messages
    """

    @property
    def other_datafile_kwargs(self) :
        return {'header_rows':self.__header_rows,
                'rows_to_skip':self.__rows_to_skip,
                'rows_to_select':self.__rows_to_select}

    def __init__(self,dirpath,
                 header_rows=LECROY_CONST.HEADER_ROWS,
                 rows_to_skip=LECROY_CONST.LECROY_FILE_ROWS_TO_SKIP,
                 rows_to_select=LECROY_CONST.LECROY_FILE_ROWS_TO_SELECT,
                 **kwargs) :
        """
        dirpath = path to the directory to watch
        header_rows = the number of rows in the raw files making up the header
        rows_to_skip = the number of rows in the raw files to completely ignore at the beginning
        rows_to_select = the number of rows to select in the raw files after the initial skip
        """
        self.__header_rows = header_rows
        self.__rows_to_skip = rows_to_skip
        self.__rows_to_select = rows_to_select
        super().__init__(dirpath,datafile_type=UploadLecroyDataFile,**kwargs)
