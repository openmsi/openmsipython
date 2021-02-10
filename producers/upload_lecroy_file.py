#imports
from ..oscilloscope.lecroy_file import LeCroyFile
from ..utilities.logging import Logger
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
    parser.add_argument('--n_threads', default=10, type=int,
                        help='Maximum number of threads to use (default=10)')
    parser.add_argument('--chunk_size', default=4096, type=int,
                        help='Size (in bytes) of chunks into which files should be broken as they are uploaded (default=4096)')
    args = parser.parse_args(args=args)
    #get the logger
    logger = Logger()
    #check the arguments
    check_args(args,logger)
    #make the LeCroyFile for the single specified file
    upload_oscilloscope_file = LeCroyFile(args.filepath,logger)
    #chunk and upload the file
    upload_oscilloscope_file.upload(args.n_threads,args.chunk_size)
    logger.info(f'Done uploading {args.filepath}')

if __name__=='__main__' :
    main()