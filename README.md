# <div align="center"> Open MSI Python Code </div>
#### <div align="center">***v0.0.1***</div>

#### <div align="center">David Elbert<sup>1</sup>, Maggie Eminizer<sup>2</sup>, Sam Tabrisky<sup>3</sup></div>

 <div align="center"><sup>1</sup>Hopkins Extreme Materials Institute (HEMI), PARADIM Materials Innovation Platform, and Dept. of Earth and Planetary Sciences, The Johns Hopkins University, Baltimore, MD, USA</div>
  <div align="center"><sup>2</sup>Institute for Data Intensive Engineering and Science (IDIES), Dept. of Physics and Astronomy, The Johns Hopkins University, Baltimore, MD, USA</div>
 <div align="center"><sup>3</sup>Depts. of Biology and Computer Science, Dartmouth College, Hanover, NH, and HEMI, The Johns Hopkins University, Baltimore, MD, USA</div> 
 <br>

## Introduction
User-friendly implementation and extension of common data streaming applications using Apache Kakfa, written in Python

Available on GitHub at https://github.com/openmsi/openmsipython

Developed for Open MSI (NSF DMREF award #1921959)

## Installation

Programs use the python implementation of the Apache Kafka API, and are designed to run on Windows machines connected to laboratory instruments. The only base requirements are Python 3.7 (the python Kafka API is not yet implemented on Windows with later versions of Python), `git`, and `pip`. 

### Quick start with miniconda3

The quickest way to get started is to use Miniconda3. Miniconda3 installers can be downloaded from [the website here](https://docs.conda.io/en/latest/miniconda.html), and installation instructions can be found on [the website here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

With Miniconda installed, next create and switch to a new environment based on Python 3.7. In a terminal window (or Anaconda Prompt in admin mode on Windows) type:

```
conda create -n py37 python=3.7
conda activate py37
```

You'll need to use that second "activate" command every time you open a Terminal window or Anaconda Prompt to switch to the `py37` environment. 

Miniconda installs `pip`, and if you need to install Git you can do so with

`conda install -c anaconda git`

(or use the instructions on [the website here](https://github.com/git-guides/install-git).)

### Cloning this repo and installing the openmsipython package

While in the `py37` environment, navigate to wherever you'd like to store this code, and type:

```
git clone https://github.com/openmsi/openmsipython.git
cd openmsipython
pip install .
cd ..
```

This will give you access to all of the console commands discussed below, as well as any of the other modules in the `openmsipython` package. If you'd like to be able to make changes to the `openmsipython` code without reinstalling, you can include the `--editable` flag in the `pip install` command.

If you like, you can check everything with:

```
python

>>> import openmsipython
```

And if that line runs without any problems then the package was installed correctly.

## Open MSI Directory Stream Service

This software provides a way to stream data to a topic in a Kafka cluster using a Windows Service called "Open MSI Directory Stream Service". The Service can be installed for all users of a particular Windows machine and, once installed, it will run automatically from when the machine boots until it is stopped and/or removed.

The Open MSI Directory Stream Service will continually monitor a specific directory for any new files that are added to it. When a new file is detected, it will break the data in the file into smaller chunks and produce each of the chunks as a message to a specific Kafka topic. The `reconstuct_data_files` program discussed below, for example, can then be used to download the messages and rebuild the files on any other machine. Other routines will soon be added to perform analyses or other manipulations of the uploaded data as soon as they are available. In other words, installing the Service turns an existing directory into a "drop box" to a particular Kafka topic.  

### Setup and installation

Setting up the Service requires a configuration file that tells the program which directory to monitor and which Kafka cluster/topic to produce the data to. Two examples of these configuration files are located [here (`test.config`)](./openmsipython/services/config_files/test.config) and [here (`prod.config`)](./openmsipython/services/config_files/prod.config). These files each contain four lines, explained below:

1. `[openmsi_directory_stream_service]` : this line begins a block in the file that contains the configuration options for the Service.
1. `file_directory = [some directory path]` : this is where you specify the path to the directory you'd like the Service to monitor. The directory must already exist, to prevent accidental continuity or duplication errors.
1. `cluster_producer_config = [name or path to another config file]` : this line tells the Service which Kafka cluster the messages should be produced to, and how the Producer should be configured, by pointing it to another configuration file that includes these details. The two example config files above each give names of files in the default location for Kafka configuraton files for this parameter: `test.config` tells the code to use [this file](./openmsipython/my_kafka/config_files/test.config) and `prod.config` tells the code to use [this file](./openmsipython/my_kafka/config_files/prod.config). In your files you have a couple options for this parameter: 
    - you could use either of these two same file names as in the example files. `test.config` will produce to the "tutorial_cluster" on Kafka for testing, and `prod.config` will produce to the "openmsi_cluster" for real production cases. 
    - you could use the name of any file that exists in `openmsipython/openmsipython/my_kafka/config_files/` when you installed the repo, or the full path to a file in any other location, that contains "`[cluster]`" and "`[producer]`" sections. If you're interested in creating one of your own configuration files like this, check [the section on config files](#more-details-on-configuration-files) below.
    - you could completely omit the `cluster_producer_config` parameter, and instead add `[cluster]` and `[producer]` sections to the file below the `[openmsi_directory_stream_service]` section. Again check [the section on config files](#more-details-on-configuration-files) below for more details on how you can do this.
1. `topic_name = [topic_name]` : this is the name of the topic in the cluster to produce messages to. 

To install the Service and start it running, type the following command in the `py37` environment in your Terminal or Admin mode Anaconda Prompt:

`manage_service install_and_start --config [path_to_config_file]`

where `[path_to_config_file]` is the path to a configuration file containing at least an `[openmsi_directory_stream_service]` section in it as described above. If that command runs successfully, you should be able to see the Service listed (and running) in the Windows Service Manager window that pops up when you type `mmc Services.msc`.

### Management, use, and output

While the Service is running, you can use the `manage_service` command to perform several actions:
1. **check the Service status** with `manage_service status`
2. **stop the Service running** with `manage_service stop`. If you temporarily stop the Service using this command, you can restart it afterward with `manage_service start`.
3. **uninstall the Service completely** with `manage_service stop_and_remove` (or, if the Service is already stopped, simply `manage_service remove`)

**Please note** that if you do need to stop the Service, it would be best to wait about five minutes after adding any new files to the watched directory to do so. There is a slight buffer time between a file being recognized in the directory and all of its messages being produced to the Kafka topic, so stopping the Service without a few minutes' delay may cause some messages to be dropped.

Starting and running the Service will create a log file called `upload_data_files_added_to_directory.log` in the watched directory. At any time you can check what's in this file to see the files that have been added to the directory and produced to the topic, along with other information.

### More user options

In addition to the location of the watched directory and the cluster/topic to produce to, you can further tune the behavior of the Service by adding other options to the `[openmsi_directory_stream_service]` section of the configuration file. These options are:
1. `n_threads = [n_threads]` : Run the Service with `[n_threads]` threads instead of the default number (5). Using fewer threads may slightly decrease CPU usage but slightly increase the lag time between a file being added and its data being produced.
1. `chunk_size = [n_bytes]` : Break files into chunks of size `[n_bytes]` bytes instead of the default 16384 bytes (must be an nonzero power of two)
1. `queue_max_size = [n_messages]` : Change the size of the intermediate queue that holds messages that haven't yet been produced from the default (3000). Making the queue larger will allow files to be recognized sooner after they are added, but may increase the lag time until they are fully produced (it may also result in Kafka errors).
1. `new_files_only = [True or False]` : Set to 'False' if you would like the Service to produce any files that already exist in the watched directory at the time it's started. By default this parameter is 'True', meaning any files that already exist in the directory when the Service is started are ignored, and only files that are newly added are produced to the topic. 

## More details on configuration files

Both the Open MSI Directory Stream Service and the other programs listed below depend on configuration files. This section gives a few more details about how these files can be formatted, the recognized sections they can contain, and options you can change using them.

In general, a configuration file is a text file with one or more distinct and named sections. Comments can be added by using lines starting with "`#`", and other whitespace in general is ignored. Each section begins with a heading line like "`[section_name]`," and beneath that heading different parameters are supplied using lines like "`[key] = [value]`". 

The different sections recognized by the `openmsipython` code are:
1. `[openmsi_directory_stream_service]` for configuring the Open MSI Directory Stream Service as described above
1. `[cluster]` to configure which Kafka cluster should be used by a program and how to connect to it. Common parameters here include:
    - `bootstrap.servers` to detail the server on which the cluster is hosted
    - `sasl.mechanism` and `security.protocol` to describe how programs are authenticated to interact with the cluster
    - `sasl.username` and `sasl.password` to provide the key and secret of an API key created for the cluster
1. `[producer]` to configure a Producer used by a program. You can add here any [parameters recognized by Kafka Producers](https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html) in general, but some of the most useful are:
    - `batch.size` to control the maximum number of messages in each batch sent to the cluster
    - `retries` to control how many times a failed message should be retried before throwing a fatal error and moving on
    - `linger.ms` to change how long a batch of messages should wait to become as full as possible before being sent to the cluster 
    - `compression.type` to add or change how batches of messages are compressed before being produced (and decompressed afterward)
    - `key.serializer` and `value.serializer` to change methods used to convert message keys and values (respectively) to byte arrays. The `openmsipython` code provides an additional option called [`DataFileChunkSerializer`](./openmsipython/my_kafka/serialization.py#L10-#L29) as a message value serializer to pack chunks of data files.
1. `[consumer]` to configure a Consumer used by a program. Again here any [parameters recognized by Kafka Consumers](https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html) in general are valid, but some of the most useful are:
    - `group.id` to group Consumers amongst one another. Giving "`new`" for this parameter will create a new group ID every time the code is run.
    - `auto.offset.reset` to tell the Consumer where in the log to start consuming messages. "`earliest`" will start at the beginning of the topic every time.
    - `fetch.min.bytes` to change how many bytes must accumulate before a batch of messages is consumed from the topic (consuming batches of messages is also subject to a timeout, so changing this parameter will only ever adjust the tradeoff between throughput and latency, but will not prevent any messages from being consumed in general)
    - `key.deserializer` and `value.deserializer` to change methods used to convert message keys and values (respectively) from byte arrays to objects. The `openmsipython` code provides an additional option called [`DataFileChunkDeserializer`](./openmsipython/my_kafka/serialization.py#L31-#L58) to convert a chunk of a data file as a byte array to a [DataFileChunk object](./openmsipython/data_file_io/data_file_chunk.py#L7).

## Other programs

The `openmsipython` code provides several platform-independent Python programs to run in addition to the Windows Service.

### upload_data_file
This module uploads a single specified file to a topic on a cluster by breaking it into chunks of a particular size and uploading those chunks in several parallel threads. To run it in the most common use case, enter the following command and arguments:

`upload_data_file [file_path] --config [config_file_path] --topic_name [topic_name]`

where `[file_path]` is the path to the text file to upload, `[config_file_path]` is the path to a config file including at least `[cluster]` and `[producer]` sections, and `[topic_name]` is the name of the topic to produce to. Running the code will produce all the chunks of the single file to the topic; the process will hang until receipts of delivery come back for every message that was produced.

Options for running the code include:
1. Changing the maximum number of parallel threads allowed to run at a time: add the `--n_threads [threads]` argument where `[threads]` is the desired number of parallel threads to allow (the default is 5 threads).
1. Changing the size of the individual file chunks: add the `--chunk_size [n_bytes]` argument where `[n_bytes]` is the desired chunk size in bytes. `[n_bytes]` must be a nonzero power of two (the default is 16384).

### upload_data_files_added_to_directory
This module uploads any files that are added to a given directory path to a topic on a cluster using the same "chunking" idea as above. This program is a platform-independent version of the Open MSI Directory Stream Service that runs interactively on the command line. To run it in the most common use case, enter the following command and arguments:

`upload_data_files_added_to_directory [directory_path] --config [config_file_path] --topic_name [name_of_topic]`

where `[directory_path]` is the path to a directory to monitor for files to upload, `[config_file_path]` is the path to a config file including at least `[cluster]` and `[producer]` sections, and `[topic_name]` is the name of the topic to produce to. Running the code will automatically enqueue any files in the directory, and any others that are added during runtime, to be produced. 

While the main process is running, a line with a "`.`" character will be printed out every several seconds to indicate the process is still alive. At any time, typing "`check`" or "`c`" into the console will print a message specifying how many total files have been enqueued or are in progress. Messages will be printed to the console showing how many chunks each file is broken into, and the progress of actually producing those chunks to the topic. The processes can be shut down by typing "`quit`" or "`q`" into the console. Note that the process won't actually shut down until all currently enqueued messages have been delivered to the broker (or returned an error). Also note that the files will have all of their chunks enqueued almost immediately, but actually producing the chunks to the cluster will take some time.

Options for running the code include:
1. Changing the maximum number of parallel threads allowed to run at a time: add the `--n_threads [threads]` argument where `[threads]` is the desired number of parallel threads to use. The default is 5 threads.
1. Changing the size of the individual file chunks: add the `--chunk_size [n_bytes]` argument where `[n_bytes]` is the desired chunk size in bytes. `[n_bytes]` must be a nonzero power of two (the default is 16384).
1. Changing the number of messages that are allowed to be internally queued at once (that is, queued before being produced): add the `--queue_max_size [n_messages]` argument where `[n_messages]` is the desired number of messages allowed in the internal queue (the default is 3000 messages). This internal queue is used to make sure that there's some buffer between recognizing a file exists to be uploaded and producing all of its associated messages to the topic; its size should be set to some number of messages such that the total size of the internal queue is capped at a few batches of messages ("`batch.size`" in the producer config). The default values supplied are well compatible.
1. Changing how often the "still alive" character is printed to the console: add the `--update_seconds [seconds]` argument where `[seconds]` is the number of seconds to wait between printing the character to the console from the main thread (the default is 30 seconds). Giving -1 for this argument disables printing the "still alive" character entirely.

### reconstruct_data_files
This module subscribes a group of consumers to a topic on a cluster and passively listens in several parallel threads for messages that are file chunks of the type produced by `upload_data_file`. It reconstructs files produced to the topic from their individual chunks and puts the reconstructed files in a specified directory. To run it in the most common use case, enter the following command and arguments:

`reconstruct_data_files [working_directory_path] --config [config_file_path] --topic_name [topic_name]`

where `[working_directory_path]` is the path to the directory that the reconstructed files should be put in (if it doesn't exist it will be created), `[config_file_path]` is the path to a config file including at least `[cluster]` and `[consumer]` sections, and `[topic_name]` is the name of the topic to subscribe to/consume messages from. 

While the main process is running, a line with a "`.`" character will be printed out every several seconds to indicate the process is still alive. At any time, typing "`check`" or "`c`" into the console will print a message specifying how many total messages have been read and how many files have been completely reconstructed. When all the messages for a single file have been received and the file is completely reconstructed, a message will be printed to the console saying what file it was. The processes can be shut down at any time by typing "`quit`" or "`q`" into the console.

Options for running the code include:
1. Changing the maximum number of parallel threads allowed to run at a time: add the `--n_threads [threads]` argument where `[threads]` is the desired number of parallel threads to use (and, also, the number of consumers to allow in the group). The default is 5 threads/consumers; increasing this number may give Kafka warnings or errors intermittently as the consumer group is rebalanced.
1. Changing how often the "still alive" character is printed to the console: add the `--update_seconds [seconds]` argument where `[seconds]` is the number of seconds to wait between printing the character to the console from the main thread (the default is 30 seconds). Giving -1 for this argument disables printing the "still alive" character entirely.

## Automatic code tests
There are several tests for the codebase already written (and more are being added over time). If you're editing the code, you can make sure it doesn't break anything currently being tested by running `python test/run_all_tests.py` from just inside the directory of the repo. If you'd like to add more tests, you can include any classes that extend `unittest.TestCase` in the `test/unittests` subdirectory, and call their files anything that starts with `test`, and the `run_all_tests.py` script will run them automatically. `run_all_tests.py` needs `pyflakes` installed, which you can get right from this repo by running `pip install . [test]` (with or without the `--editable` or `-e` flag(s)).

Some of the tests rely on static example data in `test/data`. If you need to regenerate these static test data under some new conditions (i.e., because you've changed default options someplace), you can run `python test/rebuild_test_reference_data.py` and follow the prompts it gives you to replace the necessary files.

## To-do list

The following items are currently planned to be implemented ASAP:

1. More securely managing API keys and secrets instead of hardcoding them in configuration files
1. Adding a safer and more graceful shutdown when stopping the Open MSI Directory Stream Service so that no external lag time needs to be considered
1. Allowing watching directories where large files are in the process of being created/saved instead of just directories where fully-created files are being added
1. Adding more unittest routines (Jenkins? Travis CI?)
1. Implementing other data types and serialization schemas, likely using Avro
1. Further improving logging
1. Create pypi and conda installations. Pypi method using twine here: https://github.com/bast/pypi-howto. Putting on conda-forge is a heavier lift. Need to decide if it's worth it; probably not for such an immature package.
1. Python 3.8 and 3.9 support (what's the problem now?  can this be the basis of the first unittest?)

## Questions that will arise later (inFAQs?)

1. What happens to subdirectories?  Can we watch a single “uber-directory” and then populate it with subdirectories by sample or date or student, etc?
2. What are best practices for topic creation and naming?  Should we have a new topic for each student, for each instrument, for each “kind” of data, ...?
3. Would it be possible to have an environment and dependency definition? YAML??
5. How can we efficiently and effectively protect credentials and configurations so they won’t create a vulnerability?
	* key login only
	* config files using linux and Windows standards
6. How do I know (and trust!) my data made it and is safe?
7. What if I forget and write my data to some “wrong” place?  What if I write my data to the directory twice?  
8. Should I clear my data out of the streaming directory once it’s been produced to Kafka?

