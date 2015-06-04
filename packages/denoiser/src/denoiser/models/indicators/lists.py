"""Package containing indicators lists
"""
from __future__ import division
from denoiser.models.indicators import *


class IndicatorsList(object):
    """Object handling a list of indicator of a same purpose
    """

    def __init__(self):
        self.indicators = []

    def add_indicator(self, indicator):
        self.indicators.append(indicator)

    def set_stats(self, stats):
        for indicator in self.indicators:
            if indicator.__class__.__base__ == StatsIndicator:
                indicator.set_stats(stats)

    def match(self, line):
        return self.match_rate(line) > 0

    def match_rate(self, line):
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