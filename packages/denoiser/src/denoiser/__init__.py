"""Package containing all the functions and classes needed to clean a file.

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
from __future__ import division
import logging
from denoiser.models import InlineModel, IndicatorModel, MachineLearningModel
from denoiser.text import Text


class Denoiser(object):
    """Denoiser object, able to clean a file and train related models
    """

    def __init__(self, app_config):
        self.config = app_config
        self.logger = logging.getLogger('local')

        self.inline_model = InlineModel(self.config)
        self.indicator_model = IndicatorModel(self.config)
        self.learning_model = MachineLearningModel(self.config)

        self.logger.info("Denoiser initialized")

    def cleanse(self, filename, is_csv=False):
        """Cleanse a file given its name

        Parameters:
            filename (str): Path of the file to cleanse
            is_csv (bool): Specifies if the file is a CSV

        Returns:
            dict: Text data
        """
        self.logger.debug("Cleaning "+filename+"...")
        text_data = Text(filename)

        # Parse the proper format
        if is_csv:
            text_data.read_csv()
        else:
            text_data.read_txt()

        # Clean the text
        self.inline_model.load(text_data)
        self.inline_model.correct(text_data)

        self.indicator_model.load(text_data)
        self.indicator_model.correct(text_data)

        self.learning_model.load(text_data)
        self.learning_model.correct(text_data)

        return text_data

    def train(self, dataset):
        """ Train the denoiser with a set of files

        Parameters
            dataset (list): List of files
        """
        self.logger.debug("Training denoiser...")

        # Generate datastructures from dataset
        text_dataset = [Text(f) for f in dataset]

        # Create datastructures for the whole dataset
        for text_data in text_dataset:
            self.logger.debug("Preprocessing "+text_data.filename)
            text_data.read_csv()

            # print "Loading "+text.filename+"..."
            self.inline_model.load(text_data)
            self.inline_model.correct(text_data)

            self.indicator_model.load(text_data)
            self.indicator_model.correct(text_data)

        # Load existing training data
        self.logger.debug("Training learning model...")
        self.learning_model.train(text_dataset)

        self.logger.info("Machine learning model trained")

    def generate_models(self, dataset):
        """ Generates the datastructures given a set of files

        Parameters
            dataset (list): List of files
        """
        self.logger.debug("Generating datastructures...")
        text_dataset = [Text(f) for f in dataset]

        for text_data in text_dataset:
            self.logger.debug("Processing "+text_data.filename+"...")

            text_data.read_csv()
            self.inline_model.load(text_data)

        self.logger.info("Datastructure generated")
        return 0

