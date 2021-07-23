#imports
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from threading import Lock
from ..utilities.runnable import Runnable
from ..utilities.argument_parsing import MyArgumentParser
from ..data_file_io.data_file_stream_processor import DataFileStreamProcessor
from ..submodules.pdv_analysis.pdv_analysis import PDVSpallAnalysis, PDVVelocityAnalysis
from .lecroy_data_file import DownloadLecroyDataFile
from .config import LECROY_CONST

class PDVPlotMaker(DataFileStreamProcessor,Runnable) :
    """
    Class to consume DataFileChunk messages from UploadLecroyDataFiles into memory
    and create spall/velocity plots from them when all of their data are available
    """

    @property
    def other_datafile_kwargs(self) :
        return {'header_rows':self.__header_rows}

    def __init__(self,output_dir,pdv_plot_type,config_path,topic_name,header_rows=LECROY_CONST.HEADER_ROWS,**otherkwargs) :
        self.__output_dir = output_dir
        if not self.__output_dir.is_dir() :
            self.__output_dir.mkdir(parents=True)
        super().__init__(config_path,topic_name,datafile_type=DownloadLecroyDataFile,**otherkwargs)
        self.__pdv_analysis_type = None
        if pdv_plot_type=='spall' :
            self.__pdv_analysis_type = PDVSpallAnalysis
        elif pdv_plot_type=='velocity' :
            self.__pdv_analysis_type = PDVVelocityAnalysis
        else :
            self.logger.error(f'ERROR: unrecognized pdv_plot_type {pdv_plot_type}',ValueError)
        self.__header_rows = header_rows
        self.__figure = plt.figure(figsize=(10,6),dpi=300)
        self.__thread_lock = Lock() #use to make sure only one thread is writing to the Figure at once

    def make_plots_as_available(self) :
        """
        When new files are fully available in memory, make plots of the data they contain
        """
        _,processed_data_filepaths = self.process_files_as_read()
        created_plot_paths = [self.__output_dir/self.__pdv_analysis_type.plot_file_name_from_input_file_name(pdfp.name,LECROY_CONST.SKIMMED_FILENAME_APPEND) for pdfp in processed_data_filepaths]
        return self.n_msgs_read, created_plot_paths

    def _process_downloaded_data_file(self,datafile) :
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
            with self.__thread_lock :
                analysis = self.__pdv_analysis_type(file=datafile.filepath,
                                                    time=time,
                                                    voltage=voltage,
                                                    output_dir=self.__output_dir,
                                                    N=512,
                                                    overlap_frac=0.85,
                                                    pyplot_figure=self.__figure)
                analysis.run()
                #save the plot and reset the figure
                self.__figure.savefig(self.__output_dir/self.__pdv_analysis_type.plot_file_name_from_input_file_name(datafile.filepath.name,LECROY_CONST.SKIMMED_FILENAME_APPEND),bbox_inches='tight')
                self.__figure.clear()
        except Exception as e :
            return e
        return None

    @classmethod
    def run_from_command_line(cls,args=None) :
        """
        Run the plot maker from the command line
        """
        if args is None :
            #make the argument parser
            parser = MyArgumentParser('output_dir','pdv_plot_type','config','topic_name',
                                      'n_threads','update_seconds','consumer_group_ID')
        args = parser.parse_args(args=args)
        #make the plot maker
        plot_maker = cls(args.output_dir,args.pdv_plot_type,args.config,args.topic_name,
                         n_threads=args.n_threads,
                         update_secs=args.update_seconds,
                         consumer_group_ID=args.consumer_group_ID,
                         logger_file=args.output_dir)
        #start the plot maker running (returns total number of messages read and names of plot files created)
        run_start = datetime.datetime.now()
        plot_maker.logger.info(f'Listening to the {args.topic_name} topic to find Lecroy data files and create {args.pdv_plot_type} plots')
        n_msgs,plot_filepaths = plot_maker.make_plots_as_available()
        run_stop = datetime.datetime.now()
        #shut down when that function returns
        msg = 'PDV plot maker '
        if args.output_dir is not None :
            msg+=f'writing to {args.output_dir} '
        msg+= 'shut down'
        plot_maker.logger.info(msg)
        msg = f'{n_msgs} total messages were consumed'
        if len(plot_filepaths)>0 :
            msg+=f' and the following {len(plot_filepaths)} plot file'
            msg+=' was' if len(plot_filepaths)==1 else 's were'
            msg+=' created'
        msg+=f' from {run_start} to {run_stop}'
        for fn in plot_filepaths :
            msg+=f'\n\t{fn}'
        plot_maker.logger.info(msg)

#################### MAIN METHOD TO RUN FROM COMMAND LINE ####################

def main(args=None) :
    PDVPlotMaker.run_from_command_line(args)

if __name__=='__main__' :
    main()