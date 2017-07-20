"""Package containing indicators lists

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
from denoiser.models.indicators import *


class IndicatorsList(object):
    """Object handling a list of indicator of a same purpose
    """

    def __init__(self):
        self.indicators = []

    def add_indicator(self, indicator):
        """Add an indicator to the list

        Args:
            indicator (Indicator): Indicator to add to the list
        """
        self.indicators.append(indicator)

    def set_stats(self, stats):
        """Set stats for all the StatsIndicator

        Args:
            stats (`Statistics`): Text statistics to setup
        """
        for indicator in self.indicators:
            if indicator.__class__.__base__ == StatsIndicator:
                indicator.set_stats(stats)

    def match(self, line):
        """Define if a line is matching the indicators

        Args:
            line (`Line`): Input line

        Returns:
            bool: True if line match at least one indicator
        """
        return self.match_rate(line) > 0

    def match_rate(self, line):
        """Get the ratio of match of a line

        Args:
            line (Line): Input line

        Returns:
            float: Ratio of match / number of indicators
        """
        total_ind = len(self.indicators)
        matching_ind = 0

        for indicator in self.indicators:
            if indicator.match(line):
                matching_ind += 1

        return matching_ind / total_ind


class StrongIndicatorList(IndicatorsList):
    """List of strong indicator (detecting garbage strings)
    """

    def __init__(self):
        super(StrongIndicatorList, self).__init__()

        self.add_indicator(AlphaNumIndicator())
        self.add_indicator(CardinalNumberIndicator())


class CleanIndicatorList(IndicatorsList):
    """List detecting clean lines
    """

    def __init__(self):
        super(CleanIndicatorList, self).__init__()

        self.add_indicator(CleanTextIndicator())
        self.add_indicator(TitleIndicator())
