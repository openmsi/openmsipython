#constants for data file upload/download/handling

class DataFileHandlingConstants :
    @property
    def FILE_HASH_MISMATCH_CODE(self):
        return -1 # code indicating that a file's hashes didn't match
    @property
    def FILE_SUCCESSFULLY_RECONSTRUCTED_CODE(self):
        return 1  # code indicating that a file was successfully fully reconstructed
    @property
    def FILE_IN_PROGRESS(self):
        return 0  # code indicating that a file is in the process of being reconstructed
    
DATA_FILE_HANDLING_CONST=DataFileHandlingConstants()

class RunOptionConstants :
	@property
	def DEFAULT_CONFIG_FILE(self):
		return 'test' # name of the config file that will be used by default
	@property
	def DEFAULT_TOPIC_NAME(self):
		return 'lecroy_files' # name of the topic to produce to by default
	@property
	def N_DEFAULT_UPLOAD_THREADS(self) :
		return 5      # default number of threads to use when uploading a file
	@property
	def N_DEFAULT_DOWNLOAD_THREADS(self) :
		return 5      # default number of threads to use when downloading chunks of a file
	@property
	def DEFAULT_CHUNK_SIZE(self) :
		return 16384  # default size in bytes of each file upload chunk
	@property
	def DEFAULT_MAX_UPLOAD_QUEUE_SIZE(self) :
		return 3000   # default maximum number of items allowed in the upload Queue at once
	@property
	def DEFAULT_UPDATE_SECONDS(self) :
		return 30     # how many seconds to wait by default between printing the "still alive" character/message for a running process

RUN_OPT_CONST = RunOptionConstants()