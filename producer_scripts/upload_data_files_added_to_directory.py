#imports
from ..data_file_io.data_file_directory import DataFileDirectory
from ..utilities.logging import Logger
from ..utilities.config import RUN_OPT_CONST
from argparse import ArgumentParser
import os, math, datetime

#################### MAIN SCRIPT HELPER FUNCTIONS ####################

#make sure the command line arguments are valid
def check_args(args,logger) :
    #the given directory must exist
    if not os.path.isdir(args.file_directory) :
        logger.error(f'ERROR: directory {args.file_directory} does not exist!',FileNotFoundError)
    #the chunk size has to be a nonzero power of two
    if args.chunk_size==0 or math.ceil(math.log2(args.chunk_size))!=math.floor(math.log2(args.chunk_size)) :
        logger.error(f'ERROR: chunk size {args.chunk_size} is invalid. Must be a (nonzero) power of two!',ValueError)

#################### MAIN SCRIPT ####################

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: filepath to upload
    parser.add_argument('file_directory', help='Path to the directory to watch for files to upload')
    #optional arguments
    parser.add_argument('--n_threads', default=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS, type=int,
                        help=f'Maximum number of threads to use (default={RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS})')
    parser.add_argument('--chunk_size', default=RUN_OPT_CONST.DEFAULT_CHUNK_SIZE, type=int,
                        help=f'Size (in bytes) of chunks into which files should be broken as they are uploaded (default={RUN_OPT_CONST.DEFAULT_CHUNK_SIZE})')
    parser.add_argument('--update_seconds', default=RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS, type=int,
                        help=f"""Number of seconds to wait between printing a '.' to the console to indicate the program is alive 
                                 (default={RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS})""")
    args = parser.parse_args(args=args)
    #make a new logger
    logger = Logger(os.path.basename(__file__).split('.')[0])
    #check the arguments
    check_args(args,logger)
    #make the DataFileDirectory for the specified directory
    upload_file_directory = DataFileDirectory(args.file_directory,logger=logger)
    #listen for new files in the directory and run uploads as they come in until the process is shut down
    run_start = datetime.datetime.now()
    logger.info(f'Listening for files to be added to {args.file_directory}...')
    enqueued_filenames = upload_file_directory.upload_files_as_added(n_threads=args.n_threads,chunk_size=args.chunk_size,update_seconds=args.update_seconds)
    run_stop = datetime.datetime.now()
    logger.info(f'Done listening to {args.file_directory} for files to upload')
    final_msg = f'The following {len(enqueued_filenames)} files were enqueued between {run_start} and {run_stop}:\n'
    for ef in enqueued_filenames :
        final_msg+=f'{ef}\n'
    logger.info(final_msg)

if __name__=='__main__' :
    main()
