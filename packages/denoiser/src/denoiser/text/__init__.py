"""This module contains necessary classes to parse a file in order to get the :class:`.Text` object.

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
from nltk.tokenize import word_tokenize
from unidecode import unidecode
import codecs
from collections import Counter
import csv
import logging
from numpy import mean
from denoiser.text.stats import Statistics


def tokenize(line):
    """Separate line to get clean tokens out of it

    Parameters:
        line (:func:`str`): A line of text

    Returns:
        list - List of different tokens
    """
    separators = "=+/,.:;!?%<>#()&[]{}"

    tokens = []
    tokenized_line = word_tokenize(line)  # Will get rid of most of the separators

    for word in tokenized_line:
        tmp_tokens = [unidecode(word)]

        for separator in separators:
            sep_tokens = []

            for tmp_token in tmp_tokens:
                split_token = tmp_token.split(separator)

                if len(split_token) != 1:  # Token has been split
                    # Concatening the list of token with the separator
                    tkn_sep_list = []

                    for ind, tkn in enumerate(split_token):
                        tkn_sep_list.append(tkn)

                        if ind != len(split_token) - 1:  # Avoid to add the separator at the end
                            tkn_sep_list.append(unicode(separator))

                    sep_tokens += tkn_sep_list
                else:
                    sep_tokens += split_token

            tmp_tokens = sep_tokens

        tokens += [tkn for tkn in tmp_tokens if tkn != '']

    return tokens


def clean_head_tail(word):
    """Clean head and tail of a word

    Parameters:
        word (:func:`str`): The word to clean
    Returns:
        :func:`str` - Cleaned word
    """
    cleaning_regexp = re.compile(r"^[^a-zA-Z'-]*([a-zA-Z'-](.*[a-zA-Z'-])?)[^a-zA-Z'-]*$")
    alpha_regexp = re.compile(r"[a-zA-Z]")

    word_groups = cleaning_regexp.findall(word)

    # Non matching strings are set as dirty (i.e. cannot be cleaned)
    # None is returned
    if len(word_groups) == 0:
        return None

    # Words containing no letters are set to None
    if alpha_regexp.search(word_groups[0][0]) is None:
        return None

    return word_groups[0][0]


class Text(object):
    """Stores the the text from a filename given in parameters

    Args:
        fname (str): Path to the file.

    Attributes:
        filename (:func:`str`): Name of the file.
        text (:func:`list`): List of paragraphs. Every paragraph is a list of :class:`.Line`.
        stats (:class:`.Statistics`): Statistics object.
    """

    def __init__(self, fname):
        self.filename = fname
        self.text = []
        self.contains_training_data = False

        self.stats = Statistics(["line_nb", "line_avg_length", "line_total_length", "word_avg_length",
                                 "word_total_length", "word_avg_nb", "word_total_nb"])
        self.stats.set_stat("line_nb", 0)
        self.stats.set_stat("line_avg_length", 0)
        self.stats.set_stat("line_total_length", 0)
        self.stats.set_stat("word_avg_length", 0)
        self.stats.set_stat("word_total_length", 0)
        self.stats.set_stat("word_avg_nb", 0)
        self.stats.set_stat("word_total_nb", 0)

    def read_csv(self):
        """Read a CSV file and build the associated text object

        Returns:
            `Text`
        """
        self.contains_training_data = True

        with open(self.filename, "r") as f:
            csv_reader = csv.reader(f)
            paragraph = []

            for row in csv_reader:
                if len(row) != 2:
                    if len(paragraph) != 0:
                        self.text.append(paragraph)
                        paragraph = []

                    continue

                line = unicode(row[0].decode("utf-8"))
                line = line.strip(" \t\r\n")

                if len(line) == 0:
                    if len(paragraph) != 0:
                        self.text.append(paragraph)
                        paragraph = []

                    continue

                line_object = Line(line, row[1])
                paragraph.append(line_object)

                self.stats.set_stat("line_nb", self.stats.get_stat("line_nb")+1)
                self.stats.set_stat("line_total_length", self.stats.get_stat("line_total_length")+len(line_object))
                self.stats.set_stat("word_total_nb", self.stats.get_stat("word_total_nb") + len(line_object.tokens))

                words_len = sum([len(tkn) for tkn in line_object.tokens])
                self.stats.set_stat("word_total_length", self.stats.get_stat("word_total_length") + words_len)

            if len(paragraph) != 0:
                self.text.append(paragraph)

        self.stats.set_stat("line_avg_length",
                            self.stats.get_stat("line_total_length") / self.stats.get_stat("line_nb"))
        self.stats.set_stat("word_avg_length",
                            self.stats.get_stat("word_total_length") / self.stats.get_stat("word_total_nb"))
        self.stats.set_stat("word_avg_nb",
                            self.stats.get_stat("word_total_nb") / self.stats.get_stat("line_nb"))

        logging.debug(self.filename+" read")

    def read_txt(self):
        """Read a text file and build the associated text object

        Returns:
            `Text`
        """
        self.contains_training_data = False

        with codecs.open(self.filename, "rb", encoding="utf-8") as f:
            paragraph = []

            for line in f:
                line = line.strip(" \t\r\n")

                if len(line) == 0:
                    if len(paragraph) != 0:
                        self.text.append(paragraph)
                        paragraph = []

                    continue

                line_object = Line(line)
                paragraph.append(line_object)

                self.stats.set_stat("line_nb", self.stats.get_stat("line_nb")+1)
                self.stats.set_stat("line_total_length", self.stats.get_stat("line_total_length")+len(line_object))
                self.stats.set_stat("word_total_nb", self.stats.get_stat("word_total_nb") + len(line_object.tokens))

                words_len = sum([len(tkn) for tkn in line_object.tokens])
                self.stats.set_stat("word_total_length", self.stats.get_stat("word_total_length") + words_len)

            if len(paragraph) != 0:
                self.text.append(paragraph)

        self.stats.set_stat("line_avg_length",
                            self.stats.get_stat("line_total_length") / self.stats.get_stat("line_nb"))
        self.stats.set_stat("word_avg_length",
                            self.stats.get_stat("word_total_length") / self.stats.get_stat("word_total_nb"))
        self.stats.set_stat("word_avg_nb",
                            self.stats.get_stat("word_total_nb") / self.stats.get_stat("line_nb"))

        logging.debug(self.filename+" read")

    def get_clean_lines(self):
        """Returns cleans line from the text object

        Returns:
            list: List of clean lines
        """
        lines = []

        for paragraph in self.text:
            for line in paragraph:
                if line.grade == 5:
                    lines.append(line.get_clean_line())

            if len(lines) > 0 and lines[-1] != "":
                lines.append("")

        return lines

    def get_garbage_lines(self):
        """Returns garbage lines from the text object

        Returns:
            list: List of garbage lines
        """
        lines = []

        for paragraph in self.text:
            for line in paragraph:
                if line.grade == 0:
                    lines.append(line.get_orig_line())

            if len(lines) > 0 and lines[-1] != "":
                lines.append("")

        return lines

    def get_unclassified_lines(self):
        """Returns unclassified lines from the text object

        Returns:
            list: List of unclassified lines
        """
        lines = []

        for paragraph in self.text:
            for line in paragraph:
                if line.grade % 5 != 0:  # Grade is not 0 nor 5
                    lines.append(line.get_orig_line())

            if len(lines) > 0 and lines[-1] != "":
                lines.append("")

        return lines

    def retrieve_text_score(self):
        """Returns some stats and score regarding classification

        Returns:
            dict: Dictionary containing the results
        """
        # True positive is a garbage string detected as such
        score_stats = {"FP": 0, "TP": 0, "FN": 0, "TN": 0}
        class_stats = {"classified": 0, "unclassified": 0, "unrated": 0}

        for paragraph in self.text:
            for line in paragraph:
                if line.grade != 0 and line.grade != 5:
                    class_stats["unclassified"] += 1
                    continue

                if line.result is None or line.result < 0:
                    class_stats["unrated"] += 1
                    continue

                class_stats["classified"] += 1

                if line.grade == 0:  # Line detected as garbage
                    if line.result == 1:  # Line is clean
                        score_stats["FP"] += 1  # False positive
                    else:  # Line is garbage
                        score_stats["TP"] += 1  # True postive
                else:  # Line detected as clean
                    if line.result == 1:  # Line is clean
                        score_stats["TN"] += 1  # True negative
                    else:  # Line is garbage
                        score_stats["FN"] += 1  # False negative

        # Precision
        divider_pr = score_stats["TP"] + score_stats["FP"]
        if divider_pr != 0:
            precision = score_stats["TP"] / divider_pr
        else:
            precision = 0

        # Recall
        divider_rc = score_stats["TP"] + score_stats["FN"]
        if divider_rc != 0:
            recall = score_stats["TP"] / divider_rc
        else:
            recall = 0

        # F1 score
        if precision + recall != 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0

        return {
            "class": class_stats,
            "score": {
                "precision": precision,
                "recall": recall,
                "f1": f1
            },
            "raw": score_stats
        }


class Line(object):
    """Represents a line of text and provides datastructures to handle it.

    Args:
        string (unicode): Line to parse.
        result (int): (**Optional**) Expected result for a line (either a garbage string or a clean line)

    Attributes:
        tokens (:func:`list`): List of tokens contained in the initial string. Every list element is a :func:`list` of
            3 element organized in this order `(original_token, clean_token, corrected_token)`
        pos_string (:func:`str`): Reference string containing the position of all the tokens
        result (:func:`int` or :data:`None`): Expected result for a line. Helps compute fitness (F1 score) of the
                                              algorithm
        grade (:func:`int`): Grade of a line, between 0 (garbage string) and 5 (clean line).
        stats (:func:`dict`): Dictionary containing two :class:`.Statistics` objects. Each of them compute the number of
            **lower**, **upper** and **special** characters along with **numbers**.
    """

    def __init__(self, string, result=None):
        self.tokens = [[tkn, clean_head_tail(tkn), None] for tkn in tokenize(string)]

        self.pos_string = string  # String containing the position of each token (e.g. "%0 %1%2 ... %n")
        for index, token in enumerate(self.tokens):
            self.pos_string = self.pos_string.replace(token[0], "%"+str(index), 1)

        self.result = None
        if result is not None:
            self.result = int(result)

        if sum([len(t[1]) for t in self.tokens if not t[1] is None]) == 0:
            self.grade = 0
        else:
            self.grade = 3

        self.stats = {
            "orig": Statistics(["lw_char", "up_char", "nb_char", "sp_char"]),
            "clean": None
        }

        tmp_line = re.sub(r'[a-z]', 'a', self.get_orig_line())  # Lower chars replacement
        tmp_line = re.sub(r'[A-Z]', 'A', tmp_line)  # Upper chars replacement
        tmp_line = re.sub(r'[0-9]', '0', tmp_line)  # Numbers replacement
        tmp_line = re.sub(r'[^a-zA-Z0-9 ]', '#', tmp_line)  # Special chars replacement
        line_stats = Counter(tmp_line)

        self.stats["orig"].set_stat("lw_char", line_stats["a"])
        self.stats["orig"].set_stat("up_char", line_stats["A"])
        self.stats["orig"].set_stat("nb_char", line_stats["0"])
        self.stats["orig"].set_stat("sp_char", line_stats["#"])

    def raise_grade(self):
        """Add 1 to the grade of the line (up to 5)
        """
        if self.grade < 5:
            self.grade += 1

    def decrease_grade(self):
        """Remove 1 to the grade of the line (down to 0)
        """
        if self.grade > 0:
            self.grade -= 1

    def set_garbage(self):
        """Set the grade to 0
        """
        self.grade = 0

    def set_clean(self):
        """Set the grade to 5
        """
        self.grade = 5

    def get_orig_line(self):
        """Returns the original line

        Returns:
            str: Original line
        """
        string = self.pos_string

        for index, token in reversed(list(enumerate(self.tokens))):
            string = string.replace("%"+str(index), token[0])

        return string

    def get_clean_line(self):
        """Returns the clean line

        Returns:
            str: Clean line
        """
        string = self.pos_string

        for index, token in reversed(list(enumerate(self.tokens))):
            if not token[2] is None and len(token[2]) > 0:
                string = string.replace("%"+str(index), token[2].keys()[0])
            else:  # Inline correction is not available
                if not token[1] is None:
                    string = string.replace("%"+str(index), token[1])
                else:  # Clean token does not exist, use the original token
                    string = string.replace("%"+str(index), token[0])

        return re.sub(" +", " ", string).strip()

    def get_orig_stats(self):
        """Get original stats of the line

        Returns:
            Statistics: Statistics of the original line
        """
        return self.stats["orig"]

    def get_clean_stats(self):
        """Get clean stats of the line

        Returns:
            Statistics: Statistics of the clean line
        """
        if self.stats["clean"] is None:  # Compute clean stats if it is not already done
            self.stats["clean"] = Statistics(["lw_char", "up_char", "nb_char", "sp_char"])

            tmp_line = re.sub(r'[a-z]', 'a', self.get_clean_line())  # Lower chars replacement
            tmp_line = re.sub(r'[A-Z]', 'A', tmp_line)  # Upper chars replacement
            tmp_line = re.sub(r'[0-9]', '0', tmp_line)  # Numbers replacement
            tmp_line = re.sub(r'[^a-zA-Z0-9 ]', '#', tmp_line)  # Special chars replacement
            line_stats = Counter(tmp_line)

            self.stats["clean"].set_stat("lw_char", line_stats["a"])
            self.stats["clean"].set_stat("up_char", line_stats["A"])
            self.stats["clean"].set_stat("nb_char", line_stats["0"])
            self.stats["clean"].set_stat("sp_char", line_stats["#"])

        return self.stats["clean"]

    def get_line_score(self):
        """Return a global score of the line

        Returns:
            float: Score of the line
        """
        score = 0

        if len(self.tokens) == 0:
            return score

        for token in [t[2] for t in self.tokens if not t[2] is None]:
            score += mean([s for s in token.values()])

        return score / len(self.tokens)

    def __len__(self):
        return len(self.get_orig_line())

    def __str__(self):
        return str(self.tokens) + " | " + str(self.grade)
