#imports
from ..data_file_io.data_file import UploadDataFile
from ..data_file_io.config import RUN_OPT_CONST
from ..utilities.argument_parsing import existing_file, config_path, int_power_of_two
from ..utilities.logging import Logger
from argparse import ArgumentParser
import pathlib

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: filepath to upload
    parser.add_argument('filepath', type=existing_file, help='Path to the file that should be uploaded')
    #optional arguments
    parser.add_argument('--config', default=RUN_OPT_CONST.DEFAULT_CONFIG_FILE, type=config_path,
                        help=f"""Name of config file in config_files directory, or path to a file in a different location 
                                 (default={RUN_OPT_CONST.DEFAULT_CONFIG_FILE})""")
    parser.add_argument('--topic_name', default=RUN_OPT_CONST.DEFAULT_TOPIC_NAME,
                        help=f'Name of the topic to produce to (default={RUN_OPT_CONST.DEFAULT_TOPIC_NAME})')
    parser.add_argument('--n_threads', default=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS, type=int,
                        help=f'Maximum number of threads to use (default={RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS})')
    parser.add_argument('--chunk_size', default=RUN_OPT_CONST.DEFAULT_CHUNK_SIZE, type=int_power_of_two,
                        help=f'Size (in bytes) of chunks into which files should be broken as they are uploaded (default={RUN_OPT_CONST.DEFAULT_CHUNK_SIZE})')
    args = parser.parse_args(args=args)
    #make a new logger
    filename = pathlib.Path(__file__).name.split('.')[0]
    logger = Logger(filename,filepath=(pathlib.Path(args.filepath).parent)/f'{filename}.log')
    #make the DataFile for the single specified file
    upload_file = UploadDataFile(args.filepath,logger=logger)
    #chunk and upload the file
    upload_file.upload_whole_file(args.config,args.topic_name,
                                  n_threads=args.n_threads,
                                  chunk_size=args.chunk_size)
    logger.info(f'Done uploading {args.filepath}')

if __name__=='__main__' :
    main()
