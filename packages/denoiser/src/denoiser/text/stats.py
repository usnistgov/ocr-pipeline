"""Statistic package

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


class Statistics(object):
    """Statistics of one text file
    """

    def __init__(self, stat_names):
        if type(stat_names) != list:
            raise TypeError

        self.stats = {}

        for name in stat_names:
            self.stats[name] = None

        logging.debug("Statistics initialized")

    def set_stat(self, name, value):
        if name not in self.stats:
            raise KeyError("Key '"+name+"' does not exists")

        self.stats[name] = value

    def get_stat(self, name):
        if name not in self.stats:
            raise KeyError("Key '"+name+"' does not exists")

        return self.stats[name]

    def __str__(self):
        return str(self.stats)