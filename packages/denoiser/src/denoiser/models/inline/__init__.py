"""Package containing all the main inline structures
"""
from __future__ import division
from math import floor
from numpy.lib.function_base import median
from collections import Counter
import inspect
from os.path import exists
import operator
from nltk.util import ngrams as nltk_ngrams
from denoiser.models.inline.hashing import ocr_key_list_to_str, ocr_key_hash, anagram_hash
from apputils.pickling import load, save
import re
from operator import add


def truncate_map(occurence_map):
    """Truncate an occurence map by removing uncommon iteration

    Parameters:
        occurence_map (dict): Dictionary containing word as key and occurence as value

    Returns:
        dict: Truncated map
    """
    # Get occurences distribution
    distribution = Counter(occurence_map.values())
    dist_median = median(distribution.values())

    # Compute upper bound
    limit = 0.99
    dist_upper_median = sorted([v for v in distribution.values() if v > dist_median])
    dist_upper_bound = int(floor(len(dist_upper_median) * limit))

    # Compute new distribution
    min_dist_value = dist_upper_median[dist_upper_bound - 1]
    distribution = {k: v for k, v in distribution.items() if v <= min_dist_value}

    # Return new occurence map
    return {k: v for k, v in occurence_map.items() if v in distribution.keys()}


class InlineStructure(object):
    """Abstract inline structure
    """

    def __init__(self, filename):
        self.filename = filename

        if exists(self.filename):
            self.load()

    def append_data(self, **kwargs):
        raise NotImplementedError("Function "+inspect.stack()[0][3]+" has not been implemented")

    def load(self):
        if not exists(self.filename):
            return

    def save(self):
        raise NotImplementedError("Function "+inspect.stack()[0][3]+" has not been implemented")


class NGramsStructure(InlineStructure):
    """Abstract n-gram structure
    """

    def __init__(self, filename):
        self.ngrams = Counter()
        self.ngrams_pruned = Counter()

        super(NGramsStructure, self).__init__(filename)

    def append_data(self, **kwargs):
        raise NotImplementedError("Function "+inspect.stack()[0][3]+" has not been implemented")

    def prune(self, rate):
        if rate >= 1:
            self.ngrams_pruned = self.ngrams
            return

        pruned_target = {}

        truncated_target = truncate_map(self.ngrams)
        sorted_target = sorted(truncated_target.iteritems(), key=operator.itemgetter(1), reverse=True)

        total = len(sorted_target)
        registered = 0
        current_occ = 0
        for (data, occurence) in sorted_target:
            if registered / total >= rate and occurence != current_occ:
                break

            current_occ = occurence
            pruned_target[data] = occurence
            registered += 1

        self.ngrams_pruned = Counter(pruned_target)

    def load(self):
        super(NGramsStructure, self).load()

    def save(self):
        super(NGramsStructure, self).save()


class Dictionary(InlineStructure):
    """Dictionary
    """

    def __init__(self, filename):
        self.dictionary = list()

        super(Dictionary, self).__init__(filename)

    def append_data(self, unigrams):
        word_list = []

        aspell_dict = "models/aspell.en.dict"
        with open(aspell_dict, "r") as f:
            for line in f:
                word_list.append(line.strip("\r\n"))

        plc_set = set(unigrams)
        word_set = set(word_list)

        self.dictionary = list(plc_set.intersection(word_set))
        self.save()

    def load(self):
        super(Dictionary, self).load()

        self.dictionary = load(self.filename)

    def save(self):
        save(self.dictionary, self.filename)


class Unigrams(NGramsStructure):
    """Unigrams list
    """

    def __init__(self, filename):
        self.raw_unigrams = Counter()  # Unigrams not submitted to case modification

        super(Unigrams, self).__init__(filename)

    def append_data(self, text_data):
        unigrams = [token[1] for paragraph in text_data.text for line in paragraph for token in line.tokens
                    if line.grade != 0 and not token[1] is None and len(token[1]) > 1]

        unigrams_counter = Counter(unigrams)
        self.raw_unigrams += unigrams_counter

        self.save()
        return unigrams

    def generate_low_case(self, altcase_map):
        low_unigrams = {key: 0 for key in altcase_map.keys()}

        for unigram, alt_case_list in altcase_map.items():
            low_unigrams[unigram] = sum([self.raw_unigrams[alt_case] for alt_case in alt_case_list])

        self.ngrams = Counter(low_unigrams)
        self.save()

    def load(self):
        super(Unigrams, self).load()

        data = load(self.filename)

        self.raw_unigrams = data["raw_unigrams"]
        self.ngrams = data["unigrams"]
        self.ngrams_pruned = data["unigrams_pruned"]

    def save(self):
        data = {
            "raw_unigrams": self.raw_unigrams,
            "unigrams": self.ngrams,
            "unigrams_pruned": self.ngrams_pruned
        }

        save(data, self.filename)


class Bigrams(NGramsStructure):
    """Bigrams list
    """

    def __init__(self, filename):
        super(Bigrams, self).__init__(filename)

    def append_data(self, unigrams):
        bigrams = [bigram[0].lower()+" "+bigram[1].lower() for bigram in nltk_ngrams(unigrams, 2)
                   if len(bigram[0]) > 1 and len(bigram[1]) > 1]

        self.ngrams += Counter(bigrams)
        self.prune(0.35)

        self.save()

    def load(self):
        super(Bigrams, self).load()

        data = load(self.filename)

        self.ngrams = data["bigrams"]
        self.ngrams_pruned = data["bigrams_pruned"]

    def save(self):
        data = {
            "bigrams": self.ngrams,
            "bigrams_pruned": self.ngrams_pruned
        }

        save(data, self.filename)


class AltCaseMap(InlineStructure):
    """Alternative case map
    """

    def __init__(self, filename):
        self.altcase_map = {}
        self.altcase_pruned_map = {}

        super(AltCaseMap, self).__init__(filename)

    def append_data(self, unigrams):
        _altcase_map = {unigram.lower(): set() for unigram in unigrams.keys()}

        for unigram in unigrams.keys():
            _altcase_map[unigram.lower()].add(unigram)

        self.altcase_map = {key: set(value) for key, value in _altcase_map.items()}
        self.save()

    def prune(self, unigrams_pruned):
        self.altcase_pruned_map = {unigram: self.altcase_map[unigram] for unigram in unigrams_pruned.keys()}
        self.save()

    def load(self):
        super(AltCaseMap, self).load()

        data = load(self.filename)

        self.altcase_map = data["altcase"]
        self.altcase_pruned_map = data["altcase_pruned"]

    def save(self):
        data = {
            "altcase": self.altcase_map,
            "altcase_pruned": self.altcase_pruned_map
        }

        save(data, self.filename)


class OcrKeyMap(InlineStructure):
    """OCR Key map
    """

    def __init__(self, filename):
        self.ocrkey_map = {}

        super(OcrKeyMap, self).__init__(filename)

    def append_data(self, unigrams):
        word_list = []

        aspell_dict = "models/aspell.en.dict"
        with open(aspell_dict, "r") as f:
            for line in f:
                word_list.append(line.strip("\r\n"))

        word_set = set(word_list)
        unigram_set = set(unigrams.keys())

        ocr_key_map = {ocr_key_list_to_str(ocr_key_hash(word)): set() for word in unigram_set.intersection(word_set)}

        # Every word contained in the mixed case map and the dictionary
        for word in unigram_set.intersection(word_set):
            h_list = ocr_key_hash(word)
            h_str = ocr_key_list_to_str(h_list)

            ocr_key_map[h_str].add(word)  # Add the word to the tab

        combine_struct = {key: set() for key in self.ocrkey_map.keys() + ocr_key_map.keys()}

        for key, value in self.ocrkey_map.items() + ocr_key_map.items():
            combine_struct[key] = combine_struct[key].union(value)

        self.ocrkey_map = combine_struct
        self.save()

    def load(self):
        super(OcrKeyMap, self).load()

        self.ocrkey_map = load(self.filename)

    def save(self):
        save(self.ocrkey_map, self.filename)


class AnagramMap(InlineStructure):
    """Anagram map
    """

    def __init__(self, filename):
        self.anagram_hashmap = {}
        self.anagram_alphabet = {}

        super(AnagramMap, self).__init__(filename)

    def append_data(self, bigrams, unigrams):
        anaghash_map = {anagram_hash(word): set() for word in bigrams.keys() + unigrams.keys()}

        for word in bigrams.keys() + unigrams.keys():
            anaghash_map[anagram_hash(word)].add(word)

        self.anagram_hashmap = anaghash_map

        clean_word = re.compile(r"^[a-zA-Z '-]+$")
        alphabet = set()

        for word in unigrams:
            word = " "+word+" "
            chars = [char for char in word]  # Getting letters from the word
            chars += map(add, chars[:-1], chars[1:])  # Adding bigrams to the list

            alphabet = alphabet.union([anagram_hash(char) for char in set(chars)
                                       if not clean_word.match(char) is None])

        alphabet.add(0)

        self.anagram_alphabet = alphabet
        self.save()

    def load(self):
        super(AnagramMap, self).load()

        data = load(self.filename)

        self.anagram_hashmap = data["hashmap"]
        self.anagram_alphabet = data["alphabet"]

    def save(self):
        data = {
            "hashmap": self.anagram_hashmap,
            "alphabet": self.anagram_alphabet
        }

        save(data, self.filename)