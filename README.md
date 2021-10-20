# <div align="center"> Open MSI Python Code </div>
#### <div align="center">***v0.5.0***</div>

#### <div align="center">Maggie Eminizer<sup>2</sup>, Sam Tabrisky<sup>3</sup>, David Elbert<sup>1</sup></div>

 <div align="center"><sup>1</sup>Hopkins Extreme Materials Institute (HEMI), PARADIM Materials Innovation Platform, and Dept. of Earth and Planetary Sciences, The Johns Hopkins University, Baltimore, MD, USA</div>
  <div align="center"><sup>2</sup>Institute for Data Intensive Engineering and Science (IDIES), Dept. of Physics and Astronomy, The Johns Hopkins University, Baltimore, MD, USA</div>
 <div align="center"><sup>3</sup>Depts. of Biology and Computer Science, Dartmouth College, Hanover, NH, and HEMI, The Johns Hopkins University, Baltimore, MD, USA</div> 
 <br>

## Introduction
User-friendly implementation and extension of common data streaming applications using Apache Kakfa, written in Python

Available on GitHub at https://github.com/openmsi/openmsipython

Developed for Open MSI (NSF DMREF award #1921959)

## Installation

Programs use the Python implementation of the Apache Kafka API, and are designed to run on Windows machines connected to laboratory instruments. The only base requirements are Python >=3.7, `git`, and `pip`. 

### Quick start with miniconda3

The quickest way to get started is to use Miniconda3. Miniconda3 installers can be downloaded from [the website here](https://docs.conda.io/en/latest/miniconda.html), and installation instructions can be found on [the website here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

With Miniconda installed, next create and switch to a new environment for Open MSI. In a terminal window (or Anaconda Prompt in admin mode on Windows) type:

```
conda create -n openmsi python=3
conda activate openmsi
```

This environment needs a special variable set to allow the Kafka Python code to find its dependencies on Windows (see [here](https://github.com/ContinuumIO/anaconda-issues/issues/12475) for more details), so after you've done the above, type the following commands to set the variable and then refresh the environment:

```
conda env config vars set CONDA_DLL_SEARCH_MODIFICATION_ENABLE=1
conda deactivate #this command will give a warning, that's normal
conda activate openmsi
```

You'll need to use that second "activate" command every time you open a Terminal window or Anaconda Prompt to switch to the `openmsi` environment. 

Miniconda installs `pip`, and if you need to install Git you can do so with

`conda install -c anaconda git`

(or use the instructions on [the website here](https://github.com/git-guides/install-git).)

### Cloning this repo and installing the openmsipython package

While in the `openmsi` environment, navigate to wherever you'd like to store this code, and type:

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

### Other documentation

Installing the code provides access to several programs that share a basic scheme for user interaction. These programs share the following attributes:
1. Their names correspond to names of Python Classes within the code base
1. They can be run from the command line by typing their names 
    * i.e. they are provided as "console script entry points"
    * check the relevant section of the [setup.py](./setup.py) file for a list of all that are available
1. They provide helpful logging output when run, and the most relevant of these logging messages are written to files called "[ClassName].log" in the directories relevant to the programs running
1. They can be installed as Windows Services instead of run from the bare command line

The documentation for specific programs can be found in a few locations within the repo. 

The readme file [here](./openmsipython/data_file_io/) explains programs used to upload entire arbitrary files by breaking them into chunks/producing those chunks as messages to a Kafka topic or download entire files by reading messages from the topic and writing data to disk.

The readme file [here](./openmsipython/pdv) explains programs used to upload specific portions of data in Lecroy Oscilloscope files and produce sheets of plots for PDV spall or velocity analyses.

The readme file [here](./openmsipython/my_kafka) gives more details about options for configuration files used to define which kafka cluster(s) the programs interact with and how data are produced to/consumed from topics within them.

The readme file [here](./openmsipython/services) details procedures for installing any available command-line program as a Windows Service and working with it.

The readme file [here](./test) describes the automatic testing and CI/CD setup for the project, including how to run tests interactively and add additional tests.

## To-do list

The following items are currently planned to be implemented ASAP:

1. Adding a safer and more graceful shutdown when stopping Services so that no external lag time needs to be considered
1. Allowing watching directories where large files are in the process of being created/saved instead of just directories where fully-created files are being added
1. Implementing other data types and serialization schemas, likely using Avro
1. Create pypi and conda installations. Pypi method using twine here: https://github.com/bast/pypi-howto. Putting on conda-forge is a heavier lift. Need to decide if it's worth it; probably not for such an immature package.
1. Re-implement PDV plots from a submodule

## Questions that will arise later (inFAQs?)

1. What are best practices for topic creation and naming?  Should we have a new topic for each student, for each instrument, for each “kind” of data, ...?
1. Would it be possible to have an environment and dependency definition? YAML??
1. How do I know (and trust!) my data made it and is safe?
1. What if I forget and write my data to some “wrong” place?  What if I write my data to the directory twice?  
1. Should I clear my data out of the streaming directory once it’s been produced to Kafka?

