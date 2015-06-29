# denoiser

**Author:** Philippe Dessauw, philippe.dessauw@nist.gov

**Contact:** Alden Dima, alden.dima@nist.gov

-----

The denoiser is a Python package able to **detect and remove garbage strings** from a text file. Garbage strings are 
generated during the transformation of PDF documents to text files via OCR: the conversion of images, charts and tables 
often creates spurious characters within the resulting file.

## Installation

### Packaging source files

	$> cd /path/to/denoiser
	$> python setup.py sdist

You should now see **dist** package in the main directory.

### Installing the package

	$> cd path/to/denoiser/dist
	$> pip install denoiser-*version*.tar.gz

This package is now ready to use!

## Contact

If you have any questions, comments or suggestions about this repository, please send an e-mail to Alden Dima 
(alden.dima@nist.gov).
