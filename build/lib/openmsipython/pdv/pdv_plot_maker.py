#imports
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from openmsistream import DataFileStreamProcessor
from openmsistream.utilities.config import RUN_CONST
from openmsistream.utilities import Runnable
from ..shared.argument_parsing import OpenMSIPythonArgumentParser
from .pdv_analysis import PDVSpallAnalysis, PDVVelocityAnalysis
from .lecroy_data_file import DownloadLecroyDataFile
from .config import LECROY_CONST

class PDVPlotMaker(DataFileStreamProcessor,Runnable) :
    """
    Class to consume DataFileChunk messages from UploadLecroyDataFiles into memory
    and create spall/velocity plots from them when all of their data are available
    """

    ARGUMENT_PARSER_TYPE = OpenMSIPythonArgumentParser

    @property
    def other_datafile_kwargs(self) :
        return {'header_rows':self.__header_rows}

    def __init__(self,pdv_plot_type,config_path,topic_name,
                 header_rows=LECROY_CONST.HEADER_ROWS,**otherkwargs) :
        super().__init__(config_path,topic_name,datafile_type=DownloadLecroyDataFile,**otherkwargs)
        self.__pdv_analysis_type = None
        if pdv_plot_type=='spall' :
            self.__pdv_analysis_type = PDVSpallAnalysis
        elif pdv_plot_type=='velocity' :
            self.__pdv_analysis_type = PDVVelocityAnalysis
        else :
            self.logger.error(f'ERROR: unrecognized pdv_plot_type {pdv_plot_type}',exc_type=ValueError)
        self.__header_rows = header_rows

    def make_plots_as_available(self) :
        """
        When new files are fully available in memory, make plots of the data they contain
        """
        _,_,_,processed_data_filepaths = self.process_files_as_read()
        created_plot_paths = []
        for pdfp in processed_data_filepaths :
            fn = self.__pdv_analysis_type.plot_file_name_from_input_file_name(pdfp.name,
                                                                              LECROY_CONST.SKIMMED_FILENAME_APPEND)
            created_plot_paths.append(self._output_dir/fn)
        return self.n_msgs_read, self.n_msgs_processed, created_plot_paths

    def _process_downloaded_data_file(self,datafile,lock) :
        """
        Make plots for the data in the given file
        """
        try :
            #get the raw data from the file's bytestring
            data = pd.read_csv(BytesIO(datafile.bytestring),skiprows=datafile.header_rows)
            data.columns = ['Time','Ampl']
            time = data['Time'].to_numpy()
            voltage = data['Ampl'].to_numpy()
            #run the analysis using the data
            fig = plt.figure(figsize=(10,6),dpi=300)
            analysis = self.__pdv_analysis_type(file=datafile.filepath,
                                                time=time,
                                                voltage=voltage,
                                                output_dir=self._output_dir,
                                                N=512,
                                                overlap_frac=0.85,
                                                pyplot_figure=fig)#self.__figure)
            analysis.run()
            #save the plot and close the figure
            fn = self.__pdv_analysis_type.plot_file_name_from_input_file_name(datafile.filepath.name,
                                                                              LECROY_CONST.SKIMMED_FILENAME_APPEND)
            fig.savefig(self._output_dir/fn,bbox_inches='tight')
            plt.close()
        except Exception as e :
            return e
        return None

    def _failed_processing_callback(self, datafile, lock):
        warnmsg = f'WARNING: failed to make PDV plots for {datafile.full_filepath}! The consumer will need to be rerun '
        warnmsg+= 'to re-read data from this file.'
        self.logger.warning(warnmsg)

    def _mismatched_hash_callback(self, datafile, lock):
        warnmsg = f'WARNING: hash of content for {datafile.full_filepath} is not matched to what was originally '
        warnmsg+= 'uploaded! The consumer will need to be rerun to re-read data from this file.'
        self.logger.warning(warnmsg)

    @classmethod
    def get_command_line_arguments(cls) :
        superargs,superkwargs = super().get_command_line_arguments()
        args = [*superargs,'optional_output_dir','pdv_plot_type','update_seconds']
        kwargs = {**superkwargs,
                  'config':RUN_CONST.PRODUCTION_CONFIG_FILE,
                  'topic_name':LECROY_CONST.TOPIC_NAME,
                  'n_threads':RUN_CONST.N_DEFAULT_DOWNLOAD_THREADS,
                  'consumer_group_id':'pdv_plot_maker_v1'}
        return args,kwargs

    @classmethod
    def run_from_command_line(cls,args=None) :
        """
        Run the plot maker from the command line
        """
        #make the argument parser
        parser = cls.get_argument_parser()
        args = parser.parse_args(args=args)
        #make the plot maker
        plot_maker = cls(args.output_dir,args.pdv_plot_type,args.config,args.topic_name,
                         n_threads=args.n_threads,
                         update_secs=args.update_seconds,
                         consumer_group_ID=args.consumer_group_ID,
                         logger_file=args.output_dir)
        #start the plot maker running (returns total number of messages read and names of plot files created)
        run_start = datetime.datetime.now()
        msg = f'Listening to the {args.topic_name} topic to find Lecroy data files and create '
        msg+= f'{args.pdv_plot_type} plots'
        plot_maker.logger.info(msg)
        n_read,n_processed,plot_filepaths = plot_maker.make_plots_as_available()
        plot_maker.close()
        run_stop = datetime.datetime.now()
        #shut down when that function returns
        msg = 'PDV plot maker '
        if args.output_dir is not None :
            msg+=f'writing to {args.output_dir} '
        msg+= 'shut down'
        plot_maker.logger.info(msg)
        msg = f'{n_read} total messages were consumed'
        if len(plot_filepaths)>0 :
            msg+=f', {n_processed} messages were successfully processed,'
            msg+=f' and the following {len(plot_filepaths)} plot file'
            msg+=' was' if len(plot_filepaths)==1 else 's were'
            msg+=' created'
        else :
            msg+=f' and {n_processed} messages were successfully processed'
        msg+=f' from {run_start} to {run_stop}'
        for fn in plot_filepaths :
            msg+=f'\n\t{fn}'
        plot_maker.logger.info(msg)

#################### MAIN METHOD TO RUN FROM COMMAND LINE ####################

def main(args=None) :
    PDVPlotMaker.run_from_command_line(args)

if __name__=='__main__' :
    main()