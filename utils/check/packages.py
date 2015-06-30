""" Check the presence of Python packages needed to run the pipeline

.. Authors:
    Philippe Dessauw
    philippe.dessauw@nist.gov

.. Sponsor:
    Alden Dima
    alden.dima@nist.gov
    Information Systems Group
    Software and Systems Division
    Information Technology Laboratory
    National Institute of Standards and Technology
    http://www.nist.gov/itl/ssd/is
"""
from pipeline import run_master, run_slave
import nltk

nltk.data.find('tokenizers/punkt')
