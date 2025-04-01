class LecroyConstants :
    """
    Constants for working with Lecroy oscilloscope files
    """
    @property
    def TOPIC_NAME(self) :
        return 'skimmed_lecroy_pdv_files' # name of the topic that should be produced to/consumed from
    @property
    def HEADER_ROWS(self) :
        return 5           # the number of rows making up the header to the file
    @property
    def ROWS_TO_SKIP(self) :
        return int(3.95e6) # default number of rows to skip in the beginning of raw files
    @property
    def ROWS_TO_SELECT(self) :
        return int(120e3)  # default number of rows to select after initial skip in raw files
    @property
    def SKIMMED_FILENAME_APPEND(self) :
        return '_skimmed' # string to append to filenames to indicate that they don't include all of their original data

LECROY_CONST = LecroyConstants()
