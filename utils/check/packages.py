""" Check the presence of Python packages needed to run the pipeline
"""
from pipeline import run_master, run_slave

import nltk
nltk.data.find('tokenizers/punkt')