#several sets of constant variables in one location

########################## CONSTANT SHARED VARIABLES FOR THE TUTORIAL CLUSTER AND ITS TOPIC(S) ##########################

class TutorialClusterConstants :
    @property
    def SERVER(self) :
        return 'pkc-ep9mm.us-east-2.aws.confluent.cloud:9092' 
    @property
    def SASL_MECHANISM(self) :
        return 'PLAIN'
    @property
    def SECURITY_PROTOCOL(self) :
        return 'SASL_SSL'
    @property
    def USERNAME(self) :
        return '5AZU24G7K7AKNSYS'
    @property
    def PASSWORD(self) :
        return '6H8nMfsoeqJsoBShvtC5GIWHOS6U8La22JDKrWI2BT8wZWKi8qTTHrC3ygFueC2S'
    @property
    def LECROY_FILE_TOPIC_NAME(self):
        return 'lecroy_files' #name of the lecroy file topic in the tutorial_cluster
    
TUTORIAL_CLUSTER_CONST = TutorialClusterConstants()

########################## DATA FILE HANDLING CONSTANT SHARED VARIABLES ##########################

class DataFileHandlingConstants :
    @property
    def FILE_HASH_MISMATCH_CODE(self):
        return -1 # code indicating that a file's hashes didn't match
    @property
    def FILE_SUCCESSFULLY_RECONSTRUCTED_CODE(self):
        return 1 # code indicating that a file was successfully fully reconstructed
    @property
    def FILE_IN_PROGRESS(self):
        return 0 # code indicating that a file is in the process of being reconstructed
    
DATA_FILE_HANDLING_CONST=DataFileHandlingConstants()

########################## CLASS FOR RUN OPTION CONSTANT SHARED VARIABLES ##########################

class RunOptionConstants :
    @property
    def N_DEFAULT_UPLOAD_THREADS(self):
        return 5 # default number of threads to use when uploading a file
    @property
    def N_DEFAULT_DOWNLOAD_THREADS(self):
        return 5 # default number of threads to use when reconstructing files
    @property
    def DEFAULT_CHUNK_SIZE(self) :
        return 16384 #4096 # default size in bytes of each file upload chunk
    @property
    def DEFAULT_UPDATE_SECONDS(self) :
        return 30 # how many seconds to wait by default between printing the "still alive" character/message for a running process
    
RUN_OPT_CONST=RunOptionConstants()
