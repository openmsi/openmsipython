#imports
from ..data_file_io.data_file_reconstructor import DataFileReconstructor
from ..utilities.logging import Logger
from ..utilities.config import RUN_OPT_CONST
from argparse import ArgumentParser
import os, datetime

#################### MAIN SCRIPT HELPER FUNCTIONS ####################

#make sure the command line arguments are valid
def check_args(args,logger) :
    #create the workingdir if it doesn't already exist
    if not os.path.isdir(args.workingdir) :
        os.mkdir(args.workingdir)

#################### MAIN SCRIPT ####################

def main(args=None) :
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: path to directory to hold reconstructed files
    parser.add_argument('workingdir', help='Path to the directory to hold reconstructed files')
    #optional arguments
    parser.add_argument('--n_threads', default=RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS, type=int,
                        help=f'Maximum number of threads to use (default={RUN_OPT_CONST.N_DEFAULT_DOWNLOAD_THREADS})')
    parser.add_argument('--update_seconds', default=RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS, type=int,
                        help=f"""Number of seconds to wait between printing a '.' to the console to indicate the program is alive 
                                 (default={RUN_OPT_CONST.DEFAULT_UPDATE_SECONDS})""")
    args = parser.parse_args(args=args)
    #get the logger
    logger = Logger(os.path.basename(__file__).split('.')[0])
    #check the arguments
    check_args(args,logger)
    #make the LeCroyFileReconstructor to use
    file_reconstructor = DataFileReconstructor(logger=logger)
    #start the reconstructor running (returns total number of chunks read and total number of files completely reconstructed)
    run_start = datetime.datetime.now()
    logger.info(f'Listening for files to reconstruct in {args.workingdir}')
    n_msgs,n_complete_files = file_reconstructor.run(args.workingdir,n_threads=args.n_threads,update_seconds=args.update_seconds)
    run_stop = datetime.datetime.now()
    #shut down when that function returns
    logger.info(f'File reconstructor writing to {args.workingdir} shut down')
    logger.info(f'{n_msgs} total messages were consumed and {n_complete_files} complete files were reconstructed from {run_start} to {run_stop}.')

if __name__=='__main__' :
    main()
