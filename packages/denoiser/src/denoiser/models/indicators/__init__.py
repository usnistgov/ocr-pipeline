"""List of all the different indicators used to clean a text

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
import re


class StatsIndicator(object):
    """Indicator based on statistics (match the line depending on the stats)
    """

    def __init__(self, text_stats=None):
        self.stats = text_stats

    def set_stats(self, text_stats):
        """Set statistics of the indicator based on text statistics

        Args:
            text_stats (`Statistics`): Text statistics
        """
        self.stats = text_stats

    def match(self, line):
        """Define if a line is matching the rules

        Args:
            line (Line): Input line

        Returns:
            bool: True
        """
        return True


class RegexIndicator(object):
    """Indicator based on a regexp (match the line with the given regexp)
    """

    def __init__(self, regexp):
        self.regexp = '^'+regexp+'$'

    def match(self, line):
        """Define if a line is matching the rules

        Args:
            line (Line): Input line

        Returns:
            bool: True if line match the RegExp, false otherwise
        """
        return re.match(self.regexp, line.get_clean_line())


# ==========================================
# STRONG INDICATORS
# ==========================================

class AlphaNumIndicator(StatsIndicator):
    """Indicator detecting a high number of special chars
    """

    def __init__(self, stats=None):
        self.spchar_rate = 0.6
        super(AlphaNumIndicator, self).__init__(stats)

    def match(self, line):
        return True if len(line) == 0 else line.get_clean_stats().get_stat('sp_char') / len(line) > self.spchar_rate


class CardinalNumberIndicator(RegexIndicator):
    """Indicator detecting cardinal numbers
    """

    def __init__(self):
        super(CardinalNumberIndicator, self).__init__("[0-9efEaAoOsSt.,= \\-]+")


# ==========================================
# CLEAN INDICATORS
# ==========================================

class CleanTextIndicator(StatsIndicator):
    """Indicator detecting a clean line
    """

    def __init__(self, stats=None):
        self.max_length_rate = 0.5
        self.char_rate = 0.6
        super(CleanTextIndicator, self).__init__(stats)

    def match(self, line):
        if len(line) == 0:
            return False

        return float(len(line)) >= self.stats.get_stat("line_avg_length") * self.max_length_rate \
            and (line.get_clean_stats().get_stat('lw_char') / len(line) > self.char_rate
                 or line.get_clean_stats().get_stat('up_char') / len(line) > self.char_rate)


class TitleIndicator(RegexIndicator):
    """Indicator matching a title. A title is a line beginning with an upper char and followed by lower chars or space
    """

    def __init__(self):
        super(TitleIndicator, self).__init__("[A-Z][a-z ]+")
