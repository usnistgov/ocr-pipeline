# OCR Pipeline

**Author:** Philippe Dessauw, philippe.dessauw@nist.gov
**Contact:** Alden Dima, alden.dima@nist.gov

-----

## Description

The **OCR Pipeline** (referred later as the "pipeline") is designed to convert PDF files to clean TXT files in 3 steps:

1. PDF to PNG conversion with *PythonMagick* (Python binding for ImageMagick),
2. PNG to TXT conversion using *Ocropy*,
3. TXT cleaning in order to remove all trace of garbage strings.

The pipeline is running on a distributed master/slave architecture with a *Redis* queue as a communication layer.

* One master server is reading input content to build the job queue,
* Slaves pop jobs from that queue and process them.

The software is developed by the National Institute of Standards and Technology (NIST).

*N.B.:* This software has exclusively been designed to be run on **Linux servers**. Execution on Mac and Windows has not been tested.


## Prerequisites

### Python

The pipeline is developed in *Python2* (>=2.7). You can check your version using:

	$> python2 --version

**Warning:** The pipeline is not designed to work in Python3. Make sure your path point towards a Python2 installation.

#### Virtual environment

We recommend using a Python virtual environment to ensure proper operation of the pipeline. Make sure your environment is activated at installation time.

#### Packages

There are two package that needed to be installed before installing the pipeline: **pip** and **PythonMagick**.

##### pip

This package will be used to install the packages bundled in this repository and their dependancies. No manual action is required to install dependancies.

##### PythonMagick

This package needs to be manually installed. Its version is heavily dependent on your **ImageMagick** version. Please visit http://www.imagemagick.org for more information.

### Redis

Redis needs to be installed on the master server. Redis version should be **>= 2.7**. Follow Redis installation steps at http://redis.io/download#installation.

### Ocropy

Ocropy is required to convert images to text files. The code is available at https://github.com/tmbdev/ocropy. Make sure it is downloaded and can be launched on all your slaves.

### XServer

The command `xvfb-run` should be available for our scripts. Depending on your operating system, it is not always stored in the same package. Please refer to your OS package manager to download it.

### NLTK

In order for NLTK to run properly, you need to download the **english tokenizer**. The following python code will check your NLTK installation and get the tokenizer if it is not present:

	import nltk
	
	try:
	    nltk.data.find('tokenizers/punkt')
	except:
	    nltk.download('punkt')


## Downloading the project

Once all the prerequisites are met, download the project:

1. Get the source code on Github:
	
		$> cd /path/to/workspace
		$> git clone https://github.com/usnistgov/ocr-pipeline.git

2. Configure the application:

		$> cd ocr-pipeline
		$> cp -r conf.sample conf


## Configuration

All the configuration should be put in the *conf* folder.

### app.yaml

#### root

Absolute path to the pipeline code. The project will be copied to this location when you install and run the pipeline.

#### use_sudo

Define if the script needs to use sudo to install the pipeline.

#### commands / list # PNGReader / ocropy / location

Path where you have downloaded Ocropy.

#### commands / list # PNGReader / ocropy / model

Path where you have downloaded the Ocropy model (*en-default.pyrnn.gz*).

### env.yaml

#### python / path

Path of your general Python installation.

#### python / virtualenv

Path of your virtual environment. Comment this line if not needed.

### machines.yaml

#### master

The IP address of the master is in the form of a connection string. It is formatted as a list but only the first element is relevant.

#### slaves

List of connection strings to the slaves.


## Installation

Here are the steps you have to follow to install the pipeline on your architecture machine.

1. Initialize the application on your first machine
	
		$> cd /path/to/ocr-pipeline
		$> ./utils/install.sh
		$> ./ui.sh init

2. Create data models

		$> ./ui.sh create_models /path/to/training_set

*N.B.* : Depending on your training set, this step could take some time to complete.

3. Install the pipeline on slaves and master
	
		$> ./ui.sh -r install

4. Check that everything is installed on all the machines

		$> ./ui.sh -r check


## Running the pipeline

### Incoming data

When you want to start converting a corpus of PDF files, you have to place the files in the input directory. By default, this directory is named *data.in*.

### Starting the pipeline

To start the pipeline, you just have to run `./ui.sh -r start_pipeline`. It will remotely start all the slaves and the master. 

### Output

Each time a new file has been processed, it will be put in the output directory of the master server. By default, this directory is named *data.out*.

## Contact

If you encouter any issue or bug with this software please use the [issue tracker](https://github.com/usnistgov/ocr-pipeline/issues). If you want to make some enhancement, feel free to fork this repository and submit a pull request once your new feature is ready.

If you have any questions, comments or suggestions about this repository, please send an e-mail to Alden Dima (alden.dima@nist.gov).

