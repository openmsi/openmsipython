# Python_code

- sam please write for me
	- how to setup my environment on zinc20
	- how to run the pieces of code I need to run
	- (briefly) what the code does
	- how to tell that the code has run successfully
# Introduction
Git repository containing python programs to send and receive files over confluent-kafka

## Setup

The programs require the following python packages in addition to native python ones. I use conda myself to manage them.
- python-confluent-kafka
- libsodium & pysodium
- pandas
- msgpack
- scipy
To install conda on zinc20: 
1. wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
2. ./Miniconda3-latest-Linux-x86_64.sh
3. make sure you have a .profile file and a .bashrc file with the following code in it (change stabrisky to your own directory): 
```
export PATH="~/miniconda3/bin:$PATH"
PYTHONPATH="${PYTHONPATH}:~/miniconda3/bin/python3/"
export PYTHONPATH
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/stabrisky/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/stabrisky/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/stabrisky/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/stabrisky/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
```
This code ensures conda will function correctly in the zinc20 environment.
4. Go to https://github.com/sciserver/SciScript-Python and follow the instructions to download and install SciScript-Python so you can interface with CasJobs on sciserver. Unfortunately there is no conda package for this so it has to be done manually.	

## Programs

### file_chunking_test.py
Usage: `python file_chunking_test.py /path/to/file`
This program breaks a file up into chunks (currently set to 4mb as defined by the `chunk_size` variable at the top of the code) and sends it to the kafka cluster according to the `producer` object. 
It is currently set to print the chunk number of each chunk it successfully processes. 
If it doesn't print any errors it has run successfully. Currently the only way to shut it down is to close the terminal, still working on that one.

### file_writing_test.py
Usage: `python file_writing_test.py`
This program consumes data sent by file_chunking_test.py and reconstructs the files on a home directory. As long as it is running it will process any data sent to its kafka cluster as defined by the `consumer` object. 
It checks to make sure the data format is correct so it won't write anything that isn't a file sent byfile_chunking_test so don't worry about sending other data down the pipeline while it is running.
It prints the text of each file chunk it processes so you can check that and theresulting file against the input file to see if it is working correctly.

### CasJobs_metadata_uploader.py
Usage `python CasJobs_metadata_uploader.py /path/to/file`
This program is an extremely barebones test of the sciscript python module. All it does is take a file path as a command line argument and execute a SQL query into a table in the CasJobs MyDB database.
It also creates the table to insert into, so either comment that code out or drop the table if it already exists. I am going to work on a version that deletes and recreates the table if it exists. Really this is just a proof of concept test. For further detail read the python casjobs documentation, it's very straightforward and is what I used to get started.

### upload_data_file
This module uploads a single specified text file's data to the `lecroy_files` topic on the `tutorial_cluster` by breaking it into chunks of a particular size and uploading those chunks in several parallel threads. To run it in the most common use case, enter the following command and arguments:

`python -m Python_code.producer_scripts.upload_data_file [file_path]`

where `[file_path]` is the path to the text file to upload. Running the code will produce all the chunks of the single file to the topic; the process will hang until receipts of delivery come back for every message that was produced.

Options for running the code include:
1. Changing the maximum number of parallel threads allowed to run at a time: add the `--n_threads [threads]` argument where `[threads]` is the desired number of parallel threads to allow (the default is 10 threads).
1. Changing the size of the individual file chunks: add the `--chunk_size [n_bytes]` argument where `[n_bytes]` is the desired chunk size in bytes. `[n_bytes]` must be a nonzero power of two (the default is 4096).

### reconstruct_data_files
This module subscribes to the `lecroy_files` topic on the `tutorial_cluster` and passively listens in several parallel threads for messages that are file chunks of the type produced by `upload_data_file`. It reconstructs files produced to the topic from their individual chunks and puts the reconstructed files in a specified directory. To run it in the most common use case, enter the following command and arguments:

`python -m Python_code.consumer_scripts.reconstruct_data_files [working_directory_path]`

where `[working_directory_path]` is the path to the directory that the reconstructed files should be put in (if it doesn't exist it will be created). While the main process is running, a line with a '`.`' character will be printed out every several seconds to indicate the process is still alive. At any time, typing "`check`" or "`c`" into the console will print a message specifying how many total messages have been read and how many files have been completely reconstructed. When all the messages for a single file have been received and the file is completely reconstructed, a message will be printed to the console saying what file it was. The processes can be shut down at any time by typing "`quit`" or "`q`" into the console.

Options for running the code include:
1. Changing the maximum number of parallel threads allowed to run at a time: add the `--n_threads [threads]` argument where `[threads]` is the desired number of parallel threads to use (and, also, the number of consumers to allow in the group). The default is five threads/consumers; increasing this number may give Kafka warnings or errors intermittently as the consumer group is rebalanced.
1. Changing how often the "still alive" character is printed to the console: add the `--update_seconds [seconds]` argument where `[seconds]` is the number of seconds to wait between printing the character to the console from the main thread (the default is 10 seconds).

