#imports
from ..data_file_io.upload_data_file import UploadDataFile
from ..data_file_io.download_data_file import DownloadDataFileToMemory
from .config import LECROY_CONST

class UploadLecroyDataFile(UploadDataFile) :
    """
    A Lecroy oscilloscope file to upload
    """

    @property
    def select_bytes(self):
        return self.__select_bytes
    
    def __init__(self,filepath,header_rows=LECROY_CONST.HEADER_ROWS,
                 rows_to_skip=LECROY_CONST.ROWS_TO_SKIP,
                 rows_to_select=LECROY_CONST.ROWS_TO_SELECT,
                 **kwargs) :
        super().__init__(filepath,**kwargs)
        self.__select_bytes = self.__get_select_bytes(header_rows,rows_to_skip,rows_to_select)

    def __get_select_bytes(self,header_rows,rows_to_skip,rows_to_select) :
        """
        Return the list of byte range tuples that should be uploaded (the header lines and rows in rows_to_select)
        """
        #get the number of bytes in the header, rows to skip, and rows to select
        n_header_bytes = 0
        n_rows_to_skip_bytes = 0
        n_rows_to_select_bytes = 0
        with open(self.filepath,'rb') as fp :
            for i in range(header_rows) :
                n_header_bytes+=len(fp.readline())
            for i in range(rows_to_skip-header_rows) :
                n_rows_to_skip_bytes+=len(fp.readline())
            for i in range(rows_to_select) :
                n_rows_to_select_bytes+=len(fp.readline())
        #return the ranges for the header and the selected rows
        return [(0,n_header_bytes),(n_header_bytes+n_rows_to_skip_bytes,n_header_bytes+n_rows_to_skip_bytes+n_rows_to_select_bytes)]
        
class DownloadLecroyDataFile(DownloadDataFileToMemory) :
    """
    A Lecroy oscilloscope file downloaded to memory
    """

    @property
    def header_rows(self):
        return self.__header_rows

    def __init__(self,*args,header_rows=LECROY_CONST.HEADER_ROWS,**kwargs) :
        super().__init__(*args,**kwargs)
        self.__header_rows = header_rows
