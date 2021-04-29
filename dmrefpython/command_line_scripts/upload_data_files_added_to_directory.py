#imports
from ..data_file_io.data_file_directory import DataFileDirectory
from ..data_file_io.config import RUN_OPT_CONST
from ..utilities.argument_parsing import existing_dir, config_path, int_power_of_two
from ..utilities.logging import Logger
from argparse import ArgumentParser
import pathlib, datetime

#################### FILE-SCOPE CONSTANTS ####################

DEFAULT_CONFIG_FILE = 'test'         # name of the config file that will be used by default
DEFAULT_TOPIC_NAME  = 'lecroy_files' # name of the topic to produce to by default

#################### MAIN SCRIPT ####################

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: filepath to upload
    parser.add_argument('file_directory', type=existing_dir, help='Path to the directory to watch for files to upload')
    #optional arguments
    parser.add_argument('--config', default=DEFAULT_CONFIG_FILE, type=config_path,
                        help=f'Name of config file in config_files directory, or path to a file in a different location (default={DEFAULT_CONFIG_FILE})')
    parser.add_argument('--topic_name', default=DEFAULT_TOPIC_NAME,
                        help=f'Name of the topic to produce to (default={DEFAULT_TOPIC_NAME})')
    parser.add_argument('--n_threads', default=RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS, type=int,
                        help=f'Maximum number of threads to use (default={RUN_OPT_CONST.N_DEFAULT_UPLOAD_THREADS})')
    parser.add_argument('--chunk_size', default=RUN_OPT_CONST.DEFAULT_CHUNK_SIZE, type=int_power_of_two,
                        help=f'Size (in bytes) of chunks into which files should be broken as they are uploaded (default={RUN_OPT_CONST.DEFAULT_CHUNK_SIZE})')
    parser.add_argument('--queue_max_size', default=RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE, type=int,
                        help=f"""Maximum number of items (file chunks) to allow in the upload queue at a time 
                                 (default={RUN_OPT_CONST.DEFAULT_MAX_UPLOAD_QUEUE_SIZE}). Use to limit RAM usage if necessary.""")
    parser.add_argument('--update_seconds', default=RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS, type=int,
                        help=f"""Number of seconds to wait between printing a '.' to the console to indicate the program is alive 
                                 (default={RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS})""")
    parser.add_argument('--new_files_only', action='store_true',
                         help="""Add this flag to only upload files added to the directory after this code is already running
                                 (by default files already existing in the directory at startup will be uploaded as well)""")
    args = parser.parse_args(args=args)
    #make a new logger
    filename = pathlib.Path(__file__).name.split('.')[0]
    logger = Logger(filename,filepath=pathlib.Path(args.file_directory)/f'{filename}.log')
    #make the DataFileDirectory for the specified directory
    upload_file_directory = DataFileDirectory(args.file_directory,logger=logger)
    #listen for new files in the directory and run uploads as they come in until the process is shut down
    run_start = datetime.datetime.now()
    if args.new_files_only :
        logger.info(f'Listening for files to be added to {args.file_directory}...')
    else :
        logger.info(f'Uploading files in/added to {args.file_directory}...')
    uploaded_filepaths = upload_file_directory.upload_files_as_added(args.config,args.topic_name,
                                                                     takes_user_input=True,
                                                                     n_threads=args.n_threads,
                                                                     chunk_size=args.chunk_size,
                                                                     max_queue_size=args.queue_max_size,
                                                                     update_secs=args.update_seconds,
                                                                     new_files_only=args.new_files_only)
    run_stop = datetime.datetime.now()
    logger.info(f'Done listening to {args.file_directory} for files to upload')
    final_msg = f'The following {len(uploaded_filepaths)} file'
    if len(uploaded_filepaths)==1 :
        final_msg+=' was'
    else :
        final_msg+='s were'
    final_msg+=f' uploaded between {run_start} and {run_stop}:\n'
    for fp in uploaded_filepaths :
        final_msg+=f'\t{fp}\n'
    logger.info(final_msg)

if __name__=='__main__' :
    main()
