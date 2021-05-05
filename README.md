# <div align="center"> OpenMSI Python Code </div>
#### <div align="center">***v0.0.1***</div>

#### <div align="center">Created by: David Elbert<sup>1</sup>, Maggie Eminizer<sup>2</sup>, Sam Tabrisky<sup>3</sup></div>

 <div align="center"><sup>1</sup>PARADIM Data Consortium, Center for Materials in Extreme Dynamic Environments, and Dept. of Earth and Planetary Sciences, The Johns Hopkins University, Baltimore, MD, USA</div>
  <div align="center"><sup>2</sup>Institute for Data Intensive Engineering and Science (IDIES), Dept. of Physics and Astronomy, The Johns Hopkins University, Baltimore, MD, USA</div>
 <div align="center"><sup>3</sup>Depts. of Biology and Computer Science, Dartmouth College, Hanover, NH, and Whiting School of Engineering, The Johns Hopkins University, Baltimore, MD, USA</div> 
 <br>

#### <div align="center">Correspondence to: margaret.eminizer@gmail.com</div>

## Introduction
User-friendly implementation and extension of common data streaming applications using Apache Kakfa, written in Python
Available on GitHub at https://github.com/openmsi/Python_code
Developed for Open MSI (NSF DMREF award #1921959)

## Installation

## Open MSI Directory Stream Service

## Other programs

### upload_data_file
This module uploads a single specified file to the `lecroy_files` topic on the `tutorial_cluster` by breaking it into chunks of a particular size and uploading those chunks in several parallel threads. To run it in the most common use case, enter the following command and arguments:

`python -m Python_code.command_line_scripts.upload_data_file [file_path]`

where `[file_path]` is the path to the text file to upload. Running the code will produce all the chunks of the single file to the topic; the process will hang until receipts of delivery come back for every message that was produced.

Options for running the code include:
1. Changing the maximum number of parallel threads allowed to run at a time: add the `--n_threads [threads]` argument where `[threads]` is the desired number of parallel threads to allow (the default is 5 threads).
1. Changing the size of the individual file chunks: add the `--chunk_size [n_bytes]` argument where `[n_bytes]` is the desired chunk size in bytes. `[n_bytes]` must be a nonzero power of two (the default is 16384).

### upload_data_files_added_to_directory
This module uploads any files that are added to a given directory path to the `lecroy_files` topic on the `tutorial_cluster` using the same "chunking" idea as above. To run it in the most common use case, enter the following command and arguments:

`python -m Python_code.command_line_scripts.upload_data_files_added_to_directory [directory_path]`

where `[directory_path]` is the path to a directory to monitor for files to upload. Running the code will automatically enqueue any files in the directory, and any others that are added during runtime, to be produced. While the main process is running, a line with a "`.`" character will be printed out every several seconds to indicate the process is still alive. At any time, typing "`check`" or "`c`" into the console will print a message specifying how many total files have been enqueued or are in progress. Message will be printed to the console showing how many chunks each file is broken into, and the progress of actually producing those chunks to the topic. The processes can be shut down by typing "`quit`" or "`q`" into the console. Note that the process won't actually shut down until all currently enqueued messages have been delivered to the broker (or returned an error). Also note that the files will have all of their chunks enqueued almost immediately, but actually producing the chunks to the cluster will take some time.

Options for running the code include:
1. Changing the maximum number of parallel threads allowed to run at a time: add the `--n_threads [threads]` argument where `[threads]` is the desired number of parallel threads to use. The default is 5 threads.
1. Changing the size of the individual file chunks: add the `--chunk_size [n_bytes]` argument where `[n_bytes]` is the desired chunk size in bytes. `[n_bytes]` must be a nonzero power of two (the default is 16384).
1. Changing the number of messages that are allowed to be internally queued at once (that is, queued before being produced): add the `--queue_max_size [n_messages]` argument where `[n_messages]` is the desired number of messages allowed in the internal queue (the default is 3000 messages). This internal queue is used to make sure that there's some buffer between recognizing a file exists to be uploaded and producing all of its associated messages to the topic; its size should be set to some number of messages such that the total size of the internal queue is capped at a few batches of messages ("`batch.size`" in the producer config). The default values supplied are well compatible.
1. Changing how often the "still alive" character is printed to the console: add the `--update_seconds [seconds]` argument where `[seconds]` is the number of seconds to wait between printing the character to the console from the main thread (the default is 30 seconds). Giving -1 for this argument disables printing the "still alive" character.

### reconstruct_data_files
This module subscribes a group of consumers to the `lecroy_files` topic on the `tutorial_cluster` and passively listens in several parallel threads for messages that are file chunks of the type produced by `upload_data_file`. It reconstructs files produced to the topic from their individual chunks and puts the reconstructed files in a specified directory. To run it in the most common use case, enter the following command and arguments:

`python -m Python_code.command_line_scripts.reconstruct_data_files [working_directory_path]`

where `[working_directory_path]` is the path to the directory that the reconstructed files should be put in (if it doesn't exist it will be created). While the main process is running, a line with a "`.`" character will be printed out every several seconds to indicate the process is still alive. At any time, typing "`check`" or "`c`" into the console will print a message specifying how many total messages have been read and how many files have been completely reconstructed. When all the messages for a single file have been received and the file is completely reconstructed, a message will be printed to the console saying what file it was. The processes can be shut down at any time by typing "`quit`" or "`q`" into the console.

Options for running the code include:
1. Changing the maximum number of parallel threads allowed to run at a time: add the `--n_threads [threads]` argument where `[threads]` is the desired number of parallel threads to use (and, also, the number of consumers to allow in the group). The default is 5 threads/consumers; increasing this number may give Kafka warnings or errors intermittently as the consumer group is rebalanced.
1. Changing how often the "still alive" character is printed to the console: add the `--update_seconds [seconds]` argument where `[seconds]` is the number of seconds to wait between printing the character to the console from the main thread (the default is 30 seconds). Giving -1 for this argument disables printing the "still alive" character.

## To-do list

