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

`PDVPlotMaker [output_dir] --pdv_plot_type [spall_or_velocity]`

where `[output_dir]` is the path to a directory that should hold any image files that are created, and `[spall_or_velocity]` is either the word "spall" or "velocity" depending on which type of plots should be made.

To see other optional command line arguments, run `PDVPlotMaker -h`. The Python Class defining this module is [here](./pdv_plot_maker.py).

#### Important Workflow Notes ####

Running this program is probably what users in the Laser Shock lab will be doing most often, but only one instance of it can be running at a time, and only one type of plot can be made at a time (unless multiple machines are available). So, for example, if the program has been running to generate flyer velocity plots, **you must quit the program by typing "q" or "quit" before any spall data files are created on the oscilloscope**, otherwise the program will crash trying to analyze spall data for a pullback velocity and it will be rather cumbersome to reset everything to continue analyzing data from where it left off.

Another important note is that every time the program is run it will pick up from where it left off by default. This means each file will only be analyzed one time, and if the analysis code crashes for any particular file that file will be skipped and it will be nontrivial to analyze it again in the future. Log messages will be saved describing anything that goes wrong and which files would need to be re-analyzed, but it would take some digging around to reset things and/or go backwards. 

Lastly, this program should ideally be running any time files that will be uploaded are being created on the oscilloscope. Whenever you start running `PDVPlotMaker` it will begin by trying to analyze any files that have been added to the topic since the last time it was run (again because it picks up from where it left off). This may not be an issue if you don't mind extra output or waiting a bit for the code to catch up and consume everything in the intervening, but again each of those files will only be analyzed once so it's best to have that happen when the files are collected.
