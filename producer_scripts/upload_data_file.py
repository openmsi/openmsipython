#imports
from ..data_file_io.data_file import DataFile
from ..utilities.logging import Logger
from ..utilities.config import RUN_OPT_CONST
from argparse import ArgumentParser
import os, math

#################### MAIN SCRIPT HELPER FUNCTIONS ####################

#make sure the command line arguments are valid
def check_args(args,logger) :
    #the given file must exist
    if not os.path.isfile(args.filepath) :
        logger.error(f'ERROR: file {args.filepath} does not exist!',FileNotFoundError)
    #the chunk size has to be a nonzero power of two
    if args.chunk_size==0 or math.ceil(math.log2(args.chunk_size))!=math.floor(math.log2(args.chunk_size)) :
        logger.error(f'ERROR: chunk size {args.chunk_size} is invalid. Must be a (nonzero) power of two!',ValueError)

#################### MAIN SCRIPT ####################

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: filepath to upload
    parser.add_argument('filepath', help='Path to the file that should be uploaded')
    #optional arguments
    parser.add_argument('--n_threads', default=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS, type=int,
                        help=f'Maximum number of threads to use (default={RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS})')
    parser.add_argument('--chunk_size', default=RUN_OPT_CONST.DEFAULT_CHUNK_SIZE, type=int,
                        help=f'Size (in bytes) of chunks into which files should be broken as they are uploaded (default={RUN_OPT_CONST.DEFAULT_CHUNK_SIZE})')
    args = parser.parse_args(args=args)
    #make a new logger
    logger = Logger(os.path.basename(__file__).split('.')[0])
    #check the arguments
    check_args(args,logger)
    #make the DataFile for the single specified file
    upload_file = DataFile(args.filepath,logger=logger)
    #chunk and upload the file
    upload_file.upload_whole_file(n_threads=args.n_threads,chunk_size=args.chunk_size)
    logger.info(f'Done uploading {args.filepath}')

if __name__=='__main__' :
    main()
