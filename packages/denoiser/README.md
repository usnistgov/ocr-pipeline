# denoiser

-----

The denoiser is a Python package able to **detect and remove garbage strings** from a text file. Garbage strings are generated during the transformation of PDF documents to text files: the conversion of images, charts and tables often creates unreadable characters within the resulting file.

## Installation

### Packaging source files

	$> cd /path/to/denoiser
	$> python setup.py sdist

You should now see that a **dist** package appeared in the main directory.

### Installing the package

	$> cd path/to/denoiser/dist
	$> pip install denoiser-*version*.tar.gz

You can now use this package to its full extent!

## Contact

If you have any questions, comments or suggestions about this package, please send an e-mail to philippe(dot)dessauw(at)nist(dot)gov.
