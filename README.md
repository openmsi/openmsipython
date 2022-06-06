# <div align="center"> Open MSI Python Code </div>
#### <div align="center">***v0.9.2.3***</div>

#### <div align="center">Maggie Eminizer<sup>2</sup>, Amir Sharifzadeh<sup>2</sup>, Sam Tabrisky<sup>3</sup>, Alakarthika Ulaganathan<sup>4</sup>, David Elbert<sup>1</sup></div>

 <div align="center"><sup>1</sup>Hopkins Extreme Materials Institute (HEMI), PARADIM Materials Innovation Platform, and Dept. of Earth and Planetary Sciences, The Johns Hopkins University, Baltimore, MD, USA</div>
  <div align="center"><sup>2</sup>Institute for Data Intensive Engineering and Science (IDIES), Dept. of Physics and Astronomy, The Johns Hopkins University, Baltimore, MD, USA</div>
 <div align="center"><sup>3</sup>Depts. of Biology and Computer Science, Dartmouth College, Hanover, NH, and HEMI, The Johns Hopkins University, Baltimore, MD, USA</div> 
 <div align="center"><sup>4</sup>Dept. of Applied Mathematics and Statistics, The Johns Hopkins University, Baltimore, MD, USA</div>
 <br>

## Introduction

Applications for laboratory, analysis, and computational materials data streaming using [Apache Kafka](https://kafka.apache.org/) and comprehensive data modeling using [Citrine Informatics' GEMD](https://citrineinformatics.github.io/gemd-docs/)

Available on GitHub at https://github.com/openmsi/openmsipython

Developed for Open MSI (NSF DMREF award #1921959)

## Installation

Programs use the Python implementation of the Apache Kafka API, and are designed to run on Windows machines connected to laboratory instruments. 

### Quick start with miniconda3

The quickest way to get started is to use Miniconda3. Miniconda3 installers can be downloaded from [the website here](https://docs.conda.io/en/latest/miniconda.html), and installation instructions can be found on [the website here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

With Miniconda installed, next create and switch to a new environment for Open MSI. In a terminal window (or Anaconda Prompt in admin mode on Windows) type:

```
conda create -n openmsi python=3.9
conda activate openmsi
```

Python 3.9 is the most recent minor release of Python supported by confluent-kafka on Windows 10, and is recommended for most deployments. 

You'll need to use that second "activate" command every time you open a Terminal window or Anaconda Prompt to switch to the `openmsi` environment. 

Miniconda installs `pip`, and if you need to install Git you can do so with

`conda install -c anaconda git`

(or use the instructions on [the website here](https://github.com/git-guides/install-git).)

Lastly, you will need to install the `libsodium` package through Miniconda as well, using the command

`conda install -c anaconda libsodium`

This step is required to use the [`pysodium` package](https://pypi.org/project/pysodium/), needed for encrypting messages.

#### Extra setup on Windows

##### Older versions of Windows

Python 3.9 is not supported on Windows 7 or earlier. Therefor, installations on earlier Windows systems should use Python 3.7 instead of Python 3.9, in which case, the above commands are:

```
conda create -n openmsi python=3.7
conda activate openmsi
```

`OpenMSIPython` code is transparent to the difference between Python 3.7 and 3.9 in principle, but it is recommended to use newer Windows systems that can support Python 3.9

##### Issues with DLL files

This environment needs a special variable set to allow the Kafka Python code to find its dependencies on Windows (see [here](https://github.com/ContinuumIO/anaconda-issues/issues/12475) for more details), so after you've activated your Conda environment as above, type the following commands to set the variable and then refresh the environment:

```
conda env config vars set CONDA_DLL_SEARCH_MODIFICATION_ENABLE=1
conda deactivate 
conda activate openmsi
```

Due to the wide variety of Windows builds, setting this environment variable may not solve issues stemming from the `librdkafka.dll` file seemingly missing. See [here](https://github.com/confluentinc/confluent-kafka-python/issues/1221) for more context on this problem. A fix for the most common cases is built into `OpenMSIPython` and can be found [here](./openmsipython/my_kafka/__init__.py); referencing that code may be helpful in resolving any remaining `librdkafka`/`confluent-kafka-python` issues.

Another common issue with Windows builds is a seemingly "missing" `libsodium.dll` file. If you have trouble importing `pysodium`, make sure the directory containing your `libsodium.dll` is added to your `PATH`, or that the `libsodium.dll` file is properly registered on your system.

#### Extra setup on Mac OS

Mac OS is not officially supported for `OpenMSIPython`, but if you would like to work with it you will need to install `librdkafka` using homebrew to do so. This may also require installing Xcode command line tools. You can install both of these using the commands below:

```
xcode-select --install
brew install librdkafka
```

Some Mac machines may also run into an esoteric issue related to the number of active file descriptors, which appears as repeated error messages like

`% ERROR: Local: Host resolution failure: kafka-xyz.example.com:9092/42: Failed to resolve 'kafka-xyz.example.com:9092': nodename nor servname provided, or not known (after 0ms in state CONNECT)`

when the Kafka server is otherwise available and should be fine, especially when using relatively large numbers of parallel threads. Instead of the above error, you may get `too many open files` errors.

These errors may be due to running out of file descriptors as discussed in [this known `confluent-kafka`/`librdkafka` issue](https://github.com/edenhill/kcat/issues/209): using a broker hosted on Confluent Cloud may increase the likelihood of getting errors like these, because `librdkafka` creates two separate file descriptors for each known broker regardless of whether a connection is established. If you type `ulimit -n` into a Terminal window and get an output like `256`, it's likely this is the cause. To solve this issue, you will need to increase the limit of the number of allowed file descriptors, by running `ulimit -n 4096`. If that makes the errors go away, then you might want to add that line to your shell `.profile` or `.rc` file.

### Cloning this repo and installing the openmsipython package

While in the `openmsi` environment, navigate to wherever you'd like to store this code, and type:

```
git clone https://github.com/openmsi/openmsipython.git
cd openmsipython
pip install .
cd ..
```

This will give you access to several new console commands to run openmsipython applications, as well as any of the other modules in the `openmsipython` package. If you'd like to be able to make changes to the `openmsipython` code without reinstalling, you can include the `--editable` flag in the `pip install` command. If you'd like to run the automatic code tests, you can install the optional dependencies needed with `pip install .[all]` with or without the `--editable` flag.

If you like, you can check your installation with:

```
python

>>> import openmsipython
```

and if that line runs without any problems then the package was installed correctly.

### Environment variables

Interacting with the Kafka broker, including running code tests as described [here](./test), requires that some environment variables are set on your system. If you're installing any software to run as a Windows Service (as described [here](./openmsipython/services)) then you'll be prompted to enter these variables' values, but you may find it more convenient to set them once. The environment variables are called `KAFKA_TEST_CLUSTER_USERNAME`, `KAFKA_TEST_CLUSTER_PASSWORD`, `KAFKA_PROD_CLUSTER_USERNAME`, and `KAFKA_PROD_CLUSTER_PASSWORD`. The "`TEST`" variables are used to connect to the test cluster, and must be set to successfully run the automatic code tests. The "`PROD`" variables are used to connect to the full production cluster and are only needed for fully deployed code.

You can set these environment variables in a shell `.rc` or `.profile` file if running on Linux or Mac OS. On Windows you can set them as machine environment variables using commands like `[Environment]::SetEnvironmentVariable("NAME","VALUE",[EnvironmentVariableTarget]::Machine)`. You can also set them as "User" or "Process" environment variables on Windows if you don't have the necessary permissions to set them for the "Machine". 

### Other documentation

Installing the code provides access to several programs that share a basic scheme for user interaction. These programs share the following attributes:
1. Their names correspond to names of Python Classes within the code base
1. They can be run from the command line by typing their names 
    * i.e. they are provided as "console script entry points"
    * check the relevant section of the [setup.py](./setup.py) file for a list of all that are available
1. They provide helpful logging output when run, and the most relevant of these logging messages are written to files called "[ClassName].log" in the directories relevant to the programs running
1. They can be installed as Windows Services instead of run from the bare command line

The documentation for specific programs can be found in a few locations within the repo. 

The [readme file here](./openmsipython/data_file_io/) explains programs used to upload entire arbitrary files by breaking them into chunks/producing those chunks as messages to a Kafka topic or download entire files by reading messages from the topic and writing data to disk.

The [readme file here](./openmsipython/my_kafka) explains how to enable message-layer encryption through [KafkaCrypto](https://github.com/tmcqueen-materials/kafkacrypto), and gives more details about options for configuration files used to define which kafka cluster(s) the programs interact with and how data are produced to/consumed from topics within them.

The [readme file here](./openmsipython/osn) explains how to consume files to arbitrary S3 buckets instead of saving them locally.

The [readme file here](./openmsipython/services) details procedures for installing any available command-line program as a Windows Service and working with it.

The [readme file here](./openmsipython/data_models) describes how GEMD data structures are used to model data across the different projects in the Open MSI / DMREF project.

The [readme file here](./openmsipython/pdv) explains programs used to upload specific portions of data in Lecroy Oscilloscope files and produce sheets of plots for PDV spall or velocity analyses.

The [readme file here](./test) describes the automatic testing and CI/CD setup for the project, including how to run tests interactively and add additional tests.

## To-do list

The following items are currently planned to be implemented ASAP:

1. New applications for asynchronous and repeatable stream filtering and processing (i.e. to facilitate decentralized/asynchronous lab data analysis)
1. Allowing watching directories where large files are in the process of being created/saved instead of just directories where fully-created files are being added
1. Implementing other data types and serialization schemas, likely using Avro
1. Create pypi and conda installations. Pypi method using twine here: https://github.com/bast/pypi-howto. Putting on conda-forge is a heavier lift. Need to decide if it's worth it; probably not for such an immature package.
1. Re-implement PDV plots from a submodule

## Questions that will arise later (inFAQs?)

1. What happens if we send very large files to topics to be consumed to an object store? (Might not be able to transfer GB of data at once?)
1. How robust is the object store we're using (automatic backups, etc.)
1. What if I forget and write my data to some “wrong” place?  What if I write my data to the directory twice?  
1. Should I clear my data out of the streaming directory once it’s been produced to Kafka?
