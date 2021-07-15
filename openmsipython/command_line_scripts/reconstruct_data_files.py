#imports
from ..data_file_io.data_file_directory import DataFileDownloadDirectory
from ..data_file_io.config import RUN_OPT_CONST
from ..utilities.argument_parsing import create_dir, config_path
from ..utilities.logging import Logger
from ..utilities.config import UTIL_CONST
from argparse import ArgumentParser
import pathlib, datetime, uuid

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: path to directory to hold reconstructed files
    parser.add_argument('workingdir', type=create_dir, help='Path to the directory to hold reconstructed files')
    #optional arguments
    parser.add_argument('--config', default=RUN_OPT_CONST.DEFAULT_CONFIG_FILE, type=config_path,
                        help=f"""Name of config file in config_files directory, or path to a file in a different location 
                                 (default={RUN_OPT_CONST.DEFAULT_CONFIG_FILE})""")
    parser.add_argument('--topic_name', default=RUN_OPT_CONST.DEFAULT_TOPIC_NAME,
                        help=f'Name of the topic to consume from (default={RUN_OPT_CONST.DEFAULT_TOPIC_NAME})')
    parser.add_argument('--n_threads', default=RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS, type=int,
                        help=f'Maximum number of threads to use (default={RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS})')
    parser.add_argument('--update_seconds', default=UTIL_CONST.DEFAULT_UPDATE_SECONDS, type=int,
                        help=f"""Number of seconds to wait between printing a '.' to the console to indicate the program is alive 
                                 (default={UTIL_CONST.DEFAULT_UPDATE_SECONDS})""")
    parser.add_argument('--consumer_group_ID', default=str(uuid.uuid1()),
                        help='ID to use for all consumers in the group (by default a new, unique, ID will be created)')
    args = parser.parse_args(args=args)
    #get the logger
    filename = pathlib.Path(__file__).name.split('.')[0]
    logger = Logger(filename,filepath=pathlib.Path(args.workingdir)/f'{filename}.log')
    #make the DataFileDirectory
    reconstructor_directory = DataFileDownloadDirectory(args.workingdir,args.config,args.topic_name,
                                                        n_threads=args.n_threads,
                                                        consumer_group_ID=args.consumer_group_ID,
                                                        update_secs=args.update_seconds,
                                                        logger=logger)
    #start the reconstructor running (returns total number of chunks read and total number of files completely reconstructed)
    run_start = datetime.datetime.now()
    logger.info(f'Listening for files to reconstruct in {args.workingdir}')
    n_msgs,complete_filenames = reconstructor_directory.reconstruct()
    run_stop = datetime.datetime.now()
    #shut down when that function returns
    logger.info(f'File reconstructor writing to {args.workingdir} shut down')
    msg = f'{n_msgs} total messages were consumed'
    if len(complete_filenames)>0 :
        msg+=f' and the following {len(complete_filenames)} file'
        if len(complete_filenames)==1 :
            msg+=' was'
        else :
            msg+='s were'
        msg+=' successfully reconstructed'
    msg+=f' from {run_start} to {run_stop}'
    for fn in complete_filenames :
        msg+=f'\n\t{fn}'
    logger.info(msg)

if __name__=='__main__' :
    main()
