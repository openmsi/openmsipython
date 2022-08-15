# <div align="center"> Open MSI Python Code </div>
#### <div align="center">***v0.9.4.3***</div>

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

Programs use the Python implementation of the Apache Kafka API, and are designed to run on Windows, Mac or Linux machines.  Data producers typically run on Windows or Linux computers that run collection of data on laboratory instruments; Data consumers and stream processors run on the same computers, on servers with more compute power as needed, or where storage of data is hosted.  In all these cases, Open MSI components are run in Python 3 in virtual environments or sometimes in Docker containers. Open MSI can be used interactively from the command line or run as an always available service (on Windows) or daemon (on Linux).  We recommend using a minimal installation of the conda open source package management system and environment management system. These installation instructions start with installation of conda and outline all the necessary steps to run Open MSI tools.  To run Open MSI usefully, you need to understand that data streams through *topics* served by a *broker*.  In pracitce that means you will need access to a broker running on a server or in the cloud somewhere and you will need to create topics on the broker to hold the streams.  If these concepts are new to you we suggest contacting us for assistance and/or using a simple, managed cloud solution, such as Confluent Cloud, as your broker. 

### Quick Start 
#### Overview of Installation:

Here is an outline of the installation steps that are detailed below: 

1. Install miniconda3 (if not already installed)
2. Create and use a conda virtual environment dedicated to openmsipython
3. Install libsodium in that dedicated environment
4. Install git (if not already installed)
5. (Optional: Install librdkafka manually if using a Mac)
4. Install OpenMSIPython in the dedicated environment
5. Write environment variables (usually the best choice, but optional)
6. Provision the KafkaCrypto node that should be used (if encryption is required)
7. Write a config file to use
8. Install and start the Service (Windows) or Daemon (Linux) (Usual for production use, but optional when experimenting with OpenMSIPython)

**NOTE:** Please read the entire installation section below before proceeding.  There are specific difference between instructions for Windows, Linux, Intel-MacOS, and M1-MacOS. 

#### 1. miniconda3 Installation

We recommend using miniconda3 for the lightest installation. miniconda3 installers can be downloaded from [the website here](https://docs.conda.io/en/latest/miniconda.html), and installation instructions can be found on [the website here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

#### 2. Conda Environment Creation

With Miniconda installed, create and activate a dedicated virtual environment for OpenMSI. In a terminal shell (or Anaconda Prompt in admin mode on Windows) type:

```
conda create -n openmsi python=3.9
conda activate openmsi
```
##### N.B. Different Conda Step for Older Versions of Windows:

Python 3.9 is not supported on Windows 7 or earlier. Installations on pre-Windows 10 systems should, therefore, use Python 3.7 instead of Python 3.9, in which case, replace the two commands above with:

```
conda create -n openmsi python=3.7
conda activate openmsi
```

*In principle* `OpenMSIPython` code is transparent to the difference between Python 3.7 and 3.9, but it is recommended to use newer Windows systems that can support Python 3.9

###### Issues with DLL Files:

On Windows, you need to set a special variable in the virtual environment to allow the Kafka Python code to find its dependencies (see [here](https://github.com/ContinuumIO/anaconda-issues/issues/12475) for more details). To do this, activate your Conda environment as above then type the following commands to set the variable and then refresh the environment:

```
conda env config vars set CONDA_DLL_SEARCH_MODIFICATION_ENABLE=1
conda deactivate 
conda activate openmsi
```

###### More Details about Versions:

At the time of writing, Python 3.9 is the most recent release of Python supported by confluent-kafka on Windows 10, and is recommended for most deployments. 

##### General Virtual Environment Note:

No matter the operating system, you'll need to use the second command to "activate" the openmsi environment every time you open a Terminal window or Anaconda Prompt and want to work with OpenMSIPython. 

#### 3. Install libsodium

`libsodium` is a package used for the [KafkaCrypto](https://github.com/tmcqueen-materials/kafkacrypto) package that provides the end-to-end data encryption capability of `OpenMSIPython`. Since encryption is a built-in option for `OpenMSIPython`, you must install `libsodium` even if you don't want to use encryption. Install the `libsodium` package through Miniconda using the shell command:

`conda install -c anaconda libsodium`

#### 4. Install git if necessary

If your system does not have git installed, you can do so with conda.  If you need to check to see if git is installed use:

`git --version`

If it is not present then install it with 

`conda install -c anaconda git`

#### 5. Install librdkafka for Macs (this step not required on Windows)

MacOS is not officially supported for `OpenMSIPython`, but works reliably at this time. If you would like to work with MacOS you will, however, need to install `librdkafka` using the package manager homebrew. The process is different on Intel-Chip Macs than on newer Apple-Silicon, M1 Mac.  

##### On Intel MacOS:

This may also require installing Xcode command line tools. You can install both of these using the commands below:

```
xcode-select --install
brew install librdkafka
```

##### On M1 MacOS (tested on Monterey system):

1. Change the default shell to Bash:
 
    `chsh -s /bin/bash`

2. Install Homebrew:
 
    `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

3. Add homebrew bin and sbin locations to your path:
 
    `export PATH=/opt/homebrew/bin:$PATH`
    `export PATH=/opt/homebrew/sbin:$PATH`

4. Use brew to install *librdkafka*:
 
    `brew install librdkafka`

#### 6. Clone and Install OpenMSIPython from this Repo

**Clone** this `openmsipython` github repo and change directory to openmsipython:
 
```
git clone https://github.com/openmsi/openmsipython.git
cd openmsipython/
```

##### N.B Extra Steps for M1 Macs:

*On M1 Macs you need to define system paths to allow your system find the GCC compilers used while building things. You may need to edit these steps because they refer to the specific version number of librdkafka library (1.8.2 as of this writing). If the version of librdkafka your installed in step 7 is not 1.8.2, then edit these commands to refer to the actual version installed.*
 
```
CPATH=/opt/homebrew/Cellar/librdkafka/1.8.2/include pip install confluent-kafka
C_INCLUDE_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/include LIBRARY_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/lib pip install confluent_kafka
```

#### 7. **Install** openmsipython:
 
```
pip install .
cd ..
```

If you'd like to be able to make changes to the `openmsipython` code without reinstalling, you can include the `--editable` flag in the `pip install` command. If you'd like to run the automatic code tests, you can install the optional dependencies needed with `pip install .[all]` with or without the `--editable` flag.

#### Installation Completion Note:

**This completes installation and will give you access to several new console commands to run `OpenMSIPython` applications, as well as any of the other modules in the `openmsipython` package.**

If you like, you can check your installation with:

```
python

>>> import openmsipython
```

and if that line runs without any problems then the package was installed correctly.

## Other documentation

Please refer to [the documentation on the OpenMSIStream](https://github.com/openmsi/openmsistream) package for further instructions on using programs in the OpenMSI ecosystem, including details on configuration files, environment variables, and help troubleshooting.

Installing the code provides access to several programs that share a basic scheme for user interaction. These programs share the following attributes:
1. Their names correspond to names of Python Classes within the code base
1. They can be run from the command line by typing their names 
    * i.e. they are provided as "console script entry points"
    * check the relevant section of the [setup.py](./setup.py) file for a list of all that are available
1. They provide helpful logging output when run, and the most relevant of these logging messages are written to files called "[ClassName].log" in the directories relevant to the programs running
1. They can be installed as Windows Services instead of run from the bare command line

The documentation for specific programs can be found in a few locations within the repo. 

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

## Questions that will arise later (in FAQs?)

1. What happens if we send very large files to topics to be consumed to an object store? (Might not be able to transfer GB of data at once?)
1. How robust is the object store we're using (automatic backups, etc.)
