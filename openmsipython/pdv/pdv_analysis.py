#imports
import pathlib, math, datetime, functools
from argparse import ArgumentParser
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import signal, integrate
from scipy.fft import fft, ifft
from scipy.fftpack import fftshift
import numpy as np, pandas as pd

class PDVAnalysis(ABC) :
    """
    Base class for running PDV analyses
    """

    ################### PROPERTIES ###################

    @property
    def req_time_pos(self) :
        return 50e-9 # amount of time where the difference must remain positive for the start point to
                     # be considered valid. 
    @property
    @abstractmethod
    def window_time(self) :
        pass # Not implemented in base class
    @property
    def split(self) :
        return 0.10 # how much of the window time should be before the spall event
    @property
    def expansion(self) :
        return 0.20
    @property
    @functools.lru_cache()
    def vel(self) :
        return (1550/2)*((self._phasD2/1e9)-self._cen/1e9)
    @property
    def sample_rate(self) :
        return 1./(self.__time[1]-self.__time[0])
    @property
    @abstractmethod
    def output_file_name(self) : # Not implemented in base class
        pass
    @property
    def output_plot_file_path(self) :
        return self.__output_dir/self.output_file_name
    @property
    def stft_kwargs(self) :
        return {'fs':self.sample_rate,
                'nperseg':self.__N,
                'noverlap':self.__noverlap,
                'nfft':self.__nfft,
                'boundary':None}

    ################### PUBLIC FUNCTIONS ###################

    def __init__(self,*args,**kwargs) :
        self._file = kwargs['file']
        #if the raw data are given then just set them
        if kwargs.get('time') is not None and kwargs.get('voltage') is not None :
            self.__time = kwargs.get('time')
            self.__voltage = kwargs.get('voltage')
        #otherwise read the raw data from the file
        else :
            self.__time, self.__voltage = self.__get_data_from_file(kwargs['file'],
                                                                    kwargs['rows_to_skip'],
                                                                    kwargs['nrows'])
        #set some other variables
        self.__output_dir = kwargs['output_dir']
        self.__N = kwargs['N']
        self.__noverlap = np.floor(kwargs['overlap_frac']*self.__N)
        self.__nfft = self.__N*10
        #start up the output grid plot figure
        if kwargs.get('pyplot_figure') is not None :
            self.__fig = kwargs.get('pyplot_figure')
            self.__return_fig = True
        else :
            self.__fig = plt.figure(figsize=(10,6),dpi=300)
            self.__return_fig = False
        self._ax = ((self.__fig.add_subplot(2,2,1),self.__fig.add_subplot(2,2,2)),
                    (self.__fig.add_subplot(2,2,3),self.__fig.add_subplot(2,2,4)))
        self.__fig.subplots_adjust(wspace=0.2,hspace=0.35)
        super().__init__()

    def run(self) :
        self.__plot_imported_data_spectrogram()
        self.__calculate_center_frequency()
        self.__plot_cut_time_data_spectrogram()
        self.__plot_isolated_filtered_signal_spectrogram()
        self._post_run()

    ################### PRIVATE HELPER FUNCTIONS ###################

    @abstractmethod
    def _post_run(self) : 
        """
        Not implemented in the base class, except for showing/saving the output plot
        i.e., you should call super()._post_run() at the end of implemented _post_run 
        functions to show/save the output file
        """
        if self.__return_fig :
            return
        if self.__output_dir is not None :
            if not self.output_plot_file_path.parent.is_dir() :
                self.output_plot_file_path.parent.mkdir(parents=True)
            self.__fig.savefig(self.output_plot_file_path,bbox_inches='tight')
            plt.close(self.__fig)
        else :
            self.__fig.show()

    def __get_data_from_file(self,file,rows_to_skip,nrows) :
        """
        Read raw data from a file on disk into a pandas dataframe. 
        Select data of interest and return time and voltage columns as numpy arrays
        """
        data = pd.read_csv(file,skiprows=rows_to_skip,nrows=nrows)
        data.columns = ['Time','Ampl']
        time = data['Time'].to_numpy()
        voltage = data['Ampl'].to_numpy()
        return time, voltage

    def __plot_imported_data_spectrogram(self) :
        # calculate the short time fourier transform
        self.__f,self.__t,Zxx = signal.stft(self.__voltage,**self.stft_kwargs)
        # calculate power
        self.__power = 20*(np.log10(np.abs(Zxx)))
        # plot spectrogram
        pos = self._ax[0][0].imshow(self.__power,
                                    extent=[self.__t.min()/1e-9, self.__t.max()/1e-9, 
                                            self.__f.min()/1e9, self.__f.max()/1e9],
                                    aspect='auto',
                                    origin='lower')
        self.__fig.colorbar(pos,ax=self._ax[0][0],label='Power (dB)')
        self._ax[0][0].set_xlabel('Time (ns)',fontsize=8)
        self._ax[0][0].set_ylabel('Frequency (GHz)',fontsize=8)
        self._ax[0][0].set_title('Imported Data',fontsize=8)

    def __calculate_center_frequency(self) :
        # calculate the center frequency, the upshift
        npts = self.__voltage.shape[0]
        spectra1 = fft(self.__voltage)
        spectra2 = np.abs(spectra1/npts)
        spectra3 = spectra2[0:(npts//2 + 1)]
        spectra3[1:-1] = 2*spectra3[1:-1]
        w = (self.sample_rate*np.arange(0,(npts/2)))/npts # w = frequency 
        index = np.argmax(spectra3[99:])
        self._cen = w[index+99]

    def __get_cut_time_and_voltage(self) :
        # make an array of the carrier frequency of length t
        carrier = self._cen*np.ones(len(self.__t))
        # frequency array correspoding to the max power in the spectrogram
        freq_max_power = self.__f[np.argmax(self.__power,axis=0)]   
        # difference between the signal and carrier freq
        difference = freq_max_power - carrier 
        # time derivative of the difference 
        dDdt = (np.diff(difference,n=1)/1e9)/(np.diff(self.__t,n=1)/1e-9)  
        # indices where the derivative is positive
        pos_der_idx = (dDdt > 0).nonzero()[0]    
        # average time step
        avg_time_step = np.mean(np.diff(self.__t))      
        # number of steps in the difference array where it must remain positive, rounded up
        num_steps = math.ceil(self.req_time_pos/avg_time_step)              
        # loop through the indices where the derivative is positive to find where the 
        # spall event begins. we are looking for the point where the spall signal
        # increases above the carrier frequency and stays above it for at least 50ns. 
        for idx in pos_der_idx :
            # skipping the first point in the difference array because the derivative
            # array has one less point then the difference array. check to see if all
            # points for 50ns beyond idx are positive. if they are positive, save the index
            # and break the loop. if not, continue the loop. 
            if np.sum(difference[1:][idx:idx+num_steps] > 0) == num_steps:
                event_start_idx = idx + 1
                break
        # calculate the amount of time before and after the event begins and convert to
        # the number of indices in the time and voltage arrays
        time_before = self.window_time*self.split
        time_after = self.window_time*(1-self.split)
        avg_time_step2 = np.mean(np.diff(self.__time))
        idx_before = math.ceil(time_before/avg_time_step2)
        idx_after = math.ceil(time_after/avg_time_step2)
        # find the index where the time is closest to the event start time
        event_idx = np.argmin(np.abs(((self.__time - self.__time[0]) - self.__t[event_start_idx])))
        # Remove upshift
        # index where the spall event begins in the cut data. this corresponds to 
        # 'event_idx' in the uncut data 
        self.__fixt = idx_before
        # get the starting and ending indices for the cut time and voltage
        start_idx = event_idx - idx_before
        end_idx = event_idx + idx_after
        return self.__time[start_idx:end_idx+1], self.__voltage[start_idx:end_idx+1]

    def __plot_cut_time_data_spectrogram(self) :
        self._cuttime, self.__cutvoltage = self.__get_cut_time_and_voltage()
        # calculate the short time fourier transform
        self.__cutf,self.__cutt,Zxx = signal.stft(self.__cutvoltage,**self.stft_kwargs)
        # calculate the power
        power = 20*(np.log10(np.abs(Zxx)))
        # calculate the frequency where the spall signal peaks and is lowest. for the
        # low frequency make it be non-zero
        self.__freq_peak = np.max(self.__cutf[np.argmax(power,axis=0)])
        self.__freq_low = self.__cutf[np.argmax(power,axis=0)]
        self.__freq_low = np.min(self.__freq_low[np.nonzero(self.__freq_low)])
        # plot cut time and frequency range on the first plot as a rectangle 
        anchor = [(self._cuttime[0] - self.__time[0])/1e-9,self.__freq_low*(1-self.expansion)/1e9]
        width = (self._cuttime[-1] - self._cuttime[0])/1e-9
        height = (self.__freq_peak*(1+self.expansion) - self.__freq_low*(1-self.expansion))/1e9
        win = Rectangle(anchor,width,height,
                        edgecolor='r',
                        facecolor='none',
                        linewidth=0.5,
                        linestyle='-')
        self._ax[0][0].add_patch(win)
        # plot spectrogram in cut timeframe
        c_min = np.min(power[(self.__cutf>=self.__freq_low*(1-self.expansion)) * (self.__cutf<=self.__freq_peak*(1+self.expansion))])
        c_max = np.max(power[(self.__cutf>=self.__freq_low*(1-self.expansion)) * (self.__cutf<=self.__freq_peak*(1+self.expansion))])
        pos = self._ax[0][1].imshow(power,
                                    extent=[self.__cutt.min()/1e-9, self.__cutt.max()/1e-9, 
                                            self.__cutf.min()/1e9, self.__cutf.max()/1e9],
                                    aspect='auto',
                                    origin='lower',
                                    vmin=c_min,vmax=c_max)
        self.__fig.colorbar(pos,ax=self._ax[0][1],label='Power (dB)')
        self._ax[0][1].set_xlabel('Time (ns)')
        self._ax[0][1].set_ylabel('Frequency (GHz)')
        self._ax[0][1].set_title('Cut Time')
        self._ax[0][1].set_ylim([(self.__freq_low/1e9)*(1-self.expansion),(self.__freq_peak/1e9)*(1+self.expansion)])

    def __plot_isolated_filtered_signal_spectrogram(self) :
        # filter the data
        freq = fftshift(np.arange(-len(self._cuttime[self.__fixt:])/2,len(self._cuttime[self.__fixt:])/2) * self.sample_rate/len(self._cuttime[self.__fixt:]))
        wid = 0.01e9   # 10 MHz
        order = 6       # order number,6
        filt_1 = 1-np.exp(-(freq - self._cen)**order / wid**order) - np.exp(-(freq + self._cen)**order / wid**order)
        # this filter is a sixth order Gaussian notch with an 10 MHz rejection band 
        # surrounding the beat frequency with strongest intensity in the spectrogram
        voltagefilt = ifft(fft(self.__cutvoltage[self.__fixt:]) * filt_1)  # data after fixt is filtered
        voltagefilt = np.concatenate((self.__cutvoltage[0:self.__fixt],voltagefilt))
        # isolate signal
        numpts = len(self._cuttime)
        freq = fftshift(np.arange((-numpts/2),(numpts/2)) * self.sample_rate/numpts)
        filt = (freq > self.__freq_low*(1-self.expansion)) * (freq < self.__freq_peak*(1+self.expansion))
        voltagefilt = ifft(fft(voltagefilt)*filt)           
        # plot spectrogram with the signal isolated and the upshift filtered out. need 
        # to take only the real part of the voltage in order to prevent scipy from 
        # giving a two-sided spectrogram output.  
        f,t,Zxx = signal.stft(np.real(voltagefilt),**self.stft_kwargs)
        power = 20*(np.log10(np.abs(Zxx)))
        c_min = np.min(power[(f>=self.__freq_low*(1-self.expansion)) * (f<=self.__freq_peak*(1+self.expansion))])
        c_max = np.max(power[(f>=self.__freq_low*(1-self.expansion)) * (f<=self.__freq_peak*(1+self.expansion))])
        pos = self._ax[1][0].imshow(power,
                                    extent=[t.min()/1e-9, t.max()/1e-9, f.min()/1e9, f.max()/1e9],
                                    aspect='auto',
                                    origin='lower',
                                    vmin=c_min,vmax=c_max)
        self._ax[1][0].plot(t/1e-9,f[np.argmax(power,axis=0)]/1e9,'k-',linewidth=2)
        self.__fig.colorbar(pos,ax=self._ax[1][0],label='Power (dB)')
        self._ax[1][0].set_xlabel('Time (ns)')
        self._ax[1][0].set_ylabel('Frequency (GHz)')
        self._ax[1][0].set_title('Isolate Signal and Upshift Filtered Out')
        self._ax[1][0].set_ylim([(self.__freq_low/1e9)*(1-self.expansion),(self.__freq_peak/1e9)*(1+self.expansion)])
        # calculate velocity history
        phas = np.unwrap(np.angle(voltagefilt),axis=0)
        stencil = self.sample_rate/1e9*3    # samplerate/1e9 = 80 means 80 sample per ns; 5 ns stencil
        phas = phas.reshape(phas.shape[0])
        b = -smooth_diff(math.floor(stencil))
        b = b.reshape(b.shape[1])
        a = 1
        self._phasD2 = signal.lfilter(b,a,phas)*self.sample_rate/2/np.pi    # 40*ns is smoother than 10*ns

class PDVSpallAnalysis(PDVAnalysis) :
    """
    Class to run PDV analysis for spall experiments
    """

    @staticmethod
    def plot_file_name_from_input_file_name(input_file_name,append_to_remove=None) :
        if append_to_remove is not None and input_file_name.split(".")[0].endswith(append_to_remove) :
            input_file_name = input_file_name.split('.')[0][:-len(append_to_remove)]+'.'+'.'.join(input_file_name.split('.')[1:])
        return f'pdv_spall_plots_{input_file_name.split(".")[0]}.png'
    @property
    def window_time(self) :
        return 200e-9
    @property
    def output_file_name(self) :
        return self.__class__.plot_file_name_from_input_file_name(self._file.name)

    def _post_run(self) :
        self.__plot_peak_and_pullback_velocity()
        super()._post_run()

    def __plot_peak_and_pullback_velocity(self) :
        # get the peak velocity 
        peak_velocity = np.max(self.vel)
        # get the first local minimum after the peak velocity to get the pullback
        # velocity. 'order' is the number of points on each side to compare to. 
        rel_min_idx = signal.argrelmin(self.vel,order=200)[0]    # HARD CODE ---------------
        extrema = np.append(rel_min_idx,np.argmax(self.vel))
        extrema.sort()
        pullback_idx = extrema[np.where(extrema==np.argmax(self.vel))[0][0] + 1]
        pullback_velocity = self.vel[pullback_idx]
        # plot the final velocity trace with the peak and pullback velocities. 
        t = (self._cuttime-self._cuttime[0])/1e-9
        self._ax[1][1].plot(t,self.vel,'k-')
        self._ax[1][1].plot(t[np.argmax(self.vel)],peak_velocity,'go')
        self._ax[1][1].plot(t[pullback_idx],pullback_velocity,'rs')
        self._ax[1][1].set_ylim([-30,np.max(self.vel)*1.05])
        self._ax[1][1].set_xlim([0,np.max(t)])
        self._ax[1][1].grid()
        self._ax[1][1].set_xlabel('Time (ns)')
        self._ax[1][1].set_ylabel('Velocity (m/s)')
        self._ax[1][1].set_title(self._file.stem)
        self._ax[1][1].legend(['Free surface velocity',
                               f'Peak velocity: {peak_velocity}',
                               f'Pullback velocity: {pullback_velocity}'],
                               loc='lower right',
                               fontsize=8.5)

class PDVVelocityAnalysis(PDVAnalysis) :
    """
    Class to run PDV analysis for Velocity experiments
    """

    @staticmethod
    def plot_file_name_from_input_file_name(input_file_name,append_to_remove=None) :
        if append_to_remove is not None and input_file_name.split(".")[0].endswith(append_to_remove) :
            input_file_name = input_file_name.split('.')[0][:-len(append_to_remove)]+'.'+'.'.join(input_file_name.split('.')[1:])
        return f'pdv_velocity_plots_{input_file_name.split(".")[0]}.png'
    @property
    def window_time(self) :
        return 600e-9
    @property
    def output_file_name(self) :
        return self.__class__.plot_file_name_from_input_file_name(self._file.name)
    def _post_run(self) :
        self.__plot_flyer_velocity()
        super()._post_run()

    def __plot_flyer_velocity(self) :
        # find where the velocity first goes positive. this is to cut out the large
        # artificial negative velocity at the beginning
        for i,v in enumerate(self.vel > 0):
            if v == True:
                v_pos_idx = i
                break
            else:
                continue 
        # only use the data after v_pos_idx
        t = self._cuttime[v_pos_idx:]
        t -= t[0]
        v = self.vel[v_pos_idx:]
        # get position by trapezoidal integration of velocity
        position = (integrate.cumulative_trapezoid(v,t))/1e-6
        # spacer thickness for following spall experiments
        spacer_thickness = 125    # HARD CODE -------------------------------------
        # generate area of velocity to average over
        expansion = 0.15    # HARD CODE -------------------------------------------
        pos_left = spacer_thickness*(1-expansion)
        pos_right = spacer_thickness*(1+expansion)
        pos_left_idx = np.argmin(np.abs(position-pos_left))
        pos_right_idx = np.argmin(np.abs(position-pos_right))
        # calculate impact velocity as an average. skip the first entry because the
        # velocity array is 1 longer than the position array due to the integration
        impact_vel = np.mean(v[1:][pos_left_idx:pos_right_idx])
        # plot velocity vs position. again skipping the first velocity entry to get 
        # arrays of the same length
        self._ax[1][1].plot(position,v[1:],'k-')
        self._ax[1][1].set_ylim([-30,np.max(v)*1.15])
        self._ax[1][1].set_xlim([-10,np.max(position)])
        self._ax[1][1].grid()
        self._ax[1][1].set_xlabel('Position (\u03bcm)')
        self._ax[1][1].set_ylabel('Velocity (m/s)')
        self._ax[1][1].set_title(self._file.stem)
        # plot rectangle to show averaging area
        expansion = 0.05    # HARD CODE -------------------------------------------
        anchor = [position[pos_left_idx],v[1:][pos_left_idx]*(1-expansion)]
        width = position[pos_right_idx] - position[pos_left_idx]
        height = v[1:][pos_right_idx]*(1+expansion) - v[1:][pos_left_idx]*(1-expansion)
        win = Rectangle(anchor,width,height,
                        edgecolor='r',
                        facecolor='none',
                        linewidth=1.5,
                        linestyle='-')
        self._ax[1][1].add_patch(win)
        # add legend
        self._ax[1][1].legend(['Flyer velocity',
                              f'Averaging Area\nImpact Velocity: {impact_vel}'],
                              loc='lower right',
                              fontsize=8.5)

# smooth differentiation from matlab file exchange
def smooth_diff(n):
    '''
    % A smoothed differentiation filter (digital differentiator). 
    %
    % Such a filter has the following advantages:
    % 
    % First, the filter involves both the smoothing operation and differentation operation. 
    % It can be regarded as a low-pass differention filter (digital differentiator). 
    % It is well known that the common differentiation operation amplifies the high-frequency noises.
    % Therefore, the smoothded differentiation filter would be valuable in experimental (noisy) data processing. 
    % 
    % Secondly, the filter coefficients are all convenient integers (simple units) except for an integer scaling factor,
    % as may be especially significant in some applications such as those in some single-chip microcomputers
    % or digital signal processors. 
    % 
    % Usage:
    % h=smooth_diff(n)
    % n: filter length (positive integer larger no less than 2)
    % h: filter coefficients (anti-symmetry)
    %
    % Examples:
    % smooth_demo
    %
    % Author:
    % Jianwen Luo <luojw@bme.tsinghua.edu.cn, luojw@ieee.org> 2004-11-02
    % Department of Biomedical Engineering, Department of Electrical Engineering
    % Tsinghua University, Beijing 100084, P. R. China  
    % 
    % References:
    % Usui, S.; Amidror, I., 
    % Digital Low-Pass Differentiation for Biological Signal-Processing. 
    % IEEE Transactions on Biomedical Engineering 1982, 29, (10), 686-693.
    % Luo, J. W.; Bai, J.; He, P.; Ying, K., 
    % Axial strain calculation using a low-pass digital differentiator in ultrasound elastography. 
    % IEEE Transactions on Ultrasonics Ferroelectrics and Frequency Control 2004, 51, (9), 1119-1127.
    '''
    if n>=2 and math.floor(n)==math.ceil(n):
        if n%2==1:    #is odd
            m=int(np.fix((n-1)/2))
            h=np.hstack((-np.ones((1,m)),np.array(0).reshape(1,1),np.ones((1,m))))/m/(m+1)
            return h
        else:    #is even
            m=int(np.fix(n/2))
            h=np.hstack((-np.ones((1,m)),np.ones((1,m))))/m**2
            return h
    else:    
        raise TypeError('The input parameter (n) should be a positive integer larger no less than 2.')

def parse_arguments(args=None) :
    """
    Return the parsed namespace of arguments for the main script
    """
    if args is not None :
        return args
    #make the argument parser
    parser = ArgumentParser()
    #positional argument: path to the file to analyze
    parser.add_argument('file', type=pathlib.Path, 
                        help='Path to the file to analyze')
    #optional arguments
    parser.add_argument('--output_dir', type=pathlib.Path, default=pathlib.Path(),
                        help='''Path to directory in which the output plot file should be saved 
                                (default: current directory)''')
    parser.add_argument('--exp_type', choices=['spall','velocity'], default='spall',
                        help='Type of analysis to perform ("spall" or "velocity"). Default is "spall".')
    parser.add_argument('--rows_to_skip', type=int, default=int(3.95e6),
                        help='Number of rows in full data files to skip before reading data of interest')
    parser.add_argument('--nrows', type=int, default=int(120e3),
                        help='Number of rows to select as data of interest after rows_to_skip')
    parser.add_argument('--N', type=int, default=512,
                        help='Length of each segment')
    parser.add_argument('--overlap_frac', type=float, default=0.85,
                        help='fraction of overlapped data to use in Fourier transforms')
    return parser.parse_args(args=args)

def main(args=None) :
    """
    main part of the script
    """
    #start the timer
    start_time = datetime.datetime.now()
    #parse the arguments
    args = parse_arguments(args)
    #create the analysis object based on the experiment type
    if args.exp_type=='spall' :
        analysis = PDVSpallAnalysis(**args.__dict__)
    elif args.exp_type=='velocity' :
        analysis = PDVVelocityAnalysis(**args.__dict__)
    #run the analysis to create and save the sheet of plots
    analysis.run()
    #stop the timer
    end_time = datetime.datetime.now()
    #print details of the run
    print(f'Date:               {start_time.strftime("%b %d %Y    %I:%M %p")}')
    print(f'File:               {args.file}')
    print(f'Experiment Type:    {args.exp_type.capitalize()}')
    print(f'Run Time:           {end_time - start_time}')

if __name__=='__main__' :
    main()