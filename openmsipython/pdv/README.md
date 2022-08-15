## Programs to skim and upload Lecroy files and automatically create spall/velocity plots

Files in this subdirectory provide modules that can:
1. upload portions of Lecroy oscilloscope files, and 
1. download those data to memory and analyze them to automatically produce spall or velocity plots

### LecroyFileUploadDirectory

Running this module will watch a specific directory for new files to be uploaded to it, and, when new files are detected, the relevant portions of the file will be extracted and uploaded as messages to a Kafka topic. If these messages are later downloaded to recreate files on disk, those files will have "`_skimmed`" appended to their names to indicate that they only include a small amount of the original data. To run the code in the most common use case, enter the following command and argument:

`LecroyFileUploadDirectory [directory_path]`

where `[directory_path]` is the path to a directory that should be watched for new Lecroy files to skim and upload.

To see other optional command line arguments, run `LecroyFileUploadDirectory -h`. The Python Class defining this module is [here](./lecroy_file_upload_directory.py).

### PDVPlotMaker

Running this code will read messages from a kafka topic reserved for skimmed Lecroy files into memory and automatically save a sheet of either spall or velocity plots for any fully-read file. To run the code in the most common use case, enter the following command and arguments:

`PDVPlotMaker --pdv_plot_type [spall_or_velocity]`

where `[spall_or_velocity]` is either the word "spall" or "velocity" depending on which type of plots should be made.

To see other optional command line arguments, run `PDVPlotMaker -h`. The Python Class defining this module is [here](./pdv_plot_maker.py).

#### Important Workflow Notes ####

Running this program is probably what users in the Laser Shock lab will be doing most often, but only one instance of it can be running at a time, and only one type of plot can be made at a time (unless multiple machines are available). So, for example, if the program has been running to generate flyer velocity plots, **you must quit the program by typing "q" or "quit" before any spall data files are created on the oscilloscope**, otherwise the program will crash trying to analyze spall data for a pullback velocity and it will be rather cumbersome to reset everything to continue analyzing data from where it left off.

This program should ideally be running any time files that will be uploaded are being created on the oscilloscope. Whenever you start running `PDVPlotMaker` it will begin by trying to analyze any files that have been added to the topic since the last time it was run. If you're rerunning it with the same consumer ID used in a previous run, it will also read back through the topic to get messages for files that failed to be processed. 
