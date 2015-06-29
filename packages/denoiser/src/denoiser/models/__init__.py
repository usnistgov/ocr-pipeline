"""Models package

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
from os import unlink
from sklearn.linear_model.stochastic_gradient import SGDClassifier
from denoiser.models.inline import Unigrams, Dictionary, Bigrams, AltCaseMap, OcrKeyMap, AnagramMap
from denoiser.models.inline.ranking import rate_corrections
from denoiser.models.inline.utils import init_correction_map, select_anagrams, select_ocrsims, build_candidates_list, \
    correct_case, apply_bigram_boost, select_correction, extract_paragraph_bigrams, select_lower_edit_distance, \
    select_best_alphabetical_word
from denoiser.models.machine_learning import MachineLearningFeatures, MachineLearningAlgorithm
import logging
from os.path import exists, join
from denoiser.models.indicators.lists import StrongIndicatorList, CleanIndicatorList
from apputils.fileop import file_checksum
from apputils.pickling import save, load


class AbstractModel(object):
    """Abstract model, contains main functions
    """

    def __init__(self, app_config):
        self.config = app_config
        self.logger = logging.getLogger('local')

        self.hash_filename = join(app_config["dirs"]["models_root"], app_config["models"]["hashes"])
        self.hash_list = []

        if exists(self.hash_filename):
            self.hash_list = load(self.hash_filename)

    def is_preprocessed(self, filename):
        text_id = file_checksum(filename)

        if text_id not in self.hash_list:
            self.hash_list.append(text_id)
            save(self.hash_list, self.hash_filename)
            return 0

        return 1

    def load(self, text_data):
        raise NotImplementedError()

    def correct(self, text_data):
        raise NotImplementedError()


class InlineModel(AbstractModel):
    """Model for inline data structures
    """

    def __init__(self, app_config):
        super(InlineModel, self).__init__(app_config)

        inline_models_dir = join(
            app_config["root"],
            app_config["dirs"]["models_root"],
            app_config["dirs"]["models"]["inline"]
        )
        inline_models_key = app_config["models"]["inline"]

        self.dictionary = Dictionary(join(inline_models_dir, inline_models_key["dictionary"]))

        self.unigrams = Unigrams(join(inline_models_dir, inline_models_key["unigrams"]))
        self.tmp_unigrams_filename = self.unigrams.filename + app_config["exts"]["tmp"]

        self.bigrams = Bigrams(join(inline_models_dir, inline_models_key["bigrams"]))

        self.altcase_map = AltCaseMap(join(inline_models_dir, inline_models_key["altcase"]))
        self.tmp_altcase_filename = self.altcase_map.filename + app_config["exts"]["tmp"]

        self.ocrkey_map = OcrKeyMap(join(inline_models_dir, inline_models_key["ocr_keys"]))
        self.anagram_map = AnagramMap(join(inline_models_dir, inline_models_key["anagrams"]))

    def load(self, text_data):
        if self.is_preprocessed(text_data.filename) != 0:
            self.logger.debug(text_data.filename+" already loaded: skipping it.")
            return

        tmp_u = Unigrams(self.tmp_unigrams_filename)
        word_list = tmp_u.append_data(text_data)

        self.bigrams.append_data(word_list)

        tmp_ac = AltCaseMap(self.tmp_altcase_filename)
        tmp_ac.append_data(tmp_u.raw_unigrams)

        tmp_u.generate_low_case(tmp_ac.altcase_map)

        self.ocrkey_map.append_data(tmp_u.raw_unigrams)

        # Updating data
        self.unigrams.raw_unigrams += tmp_u.raw_unigrams
        self.unigrams.ngrams += tmp_u.ngrams
        self.unigrams.prune(0.7)
        self.unigrams.save()

        combine_struct = {key: set() for key in tmp_ac.altcase_map.keys() + self.altcase_map.altcase_map.keys()}
        for key, value in tmp_ac.altcase_map.items() + self.altcase_map.altcase_map.items():
            combine_struct[key] = combine_struct[key].union(value)

        self.altcase_map.altcase_map = combine_struct
        self.altcase_map.prune(self.unigrams.ngrams_pruned)
        self.altcase_map.save()

        unlink(self.tmp_unigrams_filename)
        unlink(self.tmp_altcase_filename)

        self.anagram_map.append_data(self.bigrams.ngrams_pruned, self.unigrams.ngrams_pruned)
        self.dictionary.append_data(self.unigrams.ngrams_pruned)

        self.logger.info(text_data.filename+"'s datastructures loaded")

    def correct(self, text_data):
        correction_data = self.correction_data()

        for paragraph in text_data.text:
            for line in paragraph:
                for token in line.tokens:
                    token[2] = init_correction_map(token[1], correction_data["dictionary"])

                    # Skip some correction steps if the token is too short, in the dictionary or already identified as
                    # garbage
                    if not token[2] is None and len(token[2]) == 0:
                        anagrams = select_anagrams(token[1], correction_data)
                        ocr_sims = select_ocrsims(token[1], correction_data)

                        token[2] = build_candidates_list(token[1], anagrams, ocr_sims, correction_data)
                        token[2] = correct_case(token[1], token[2], correction_data)

                        token[2] = rate_corrections(token[2])

                        if len(token[2]) == 0:  # No correction has been found
                            token[2] = None

            # Applying the bigram boost to the tokens
            bigrams = extract_paragraph_bigrams(paragraph)
            apply_bigram_boost(paragraph, bigrams, correction_data["occurence_map"])

            # Select the appropriate correction
            for line in paragraph:
                for token in line.tokens:
                    token[2] = select_correction(token[1], token[2])

                    if token[2] is not None and len(token[2]) > 1:
                        tkn_list = [tkn for tkn, sc in token[2].items() if sc == max(token[2].values())]

                        if len(tkn_list) != 1:
                            tkn_list = select_lower_edit_distance(token[1], {tkn: token[2][tkn] for tkn in tkn_list})

                        if len(tkn_list) != 1:
                            tkn_list = [select_best_alphabetical_word(token[1], tkn_list)]

                        token[2] = {tkn: token[2][tkn] for tkn in tkn_list}

    def correction_data(self):
        return {
            "occurence_map": self.unigrams.ngrams + self.bigrams.ngrams,
            "altcase": self.altcase_map.altcase_map,
            "ocrkeys": self.ocrkey_map.ocrkey_map,
            "anagrams": self.anagram_map.anagram_hashmap,
            "alphabet": self.anagram_map.anagram_alphabet,
            "dictionary": self.dictionary.dictionary
        }


class IndicatorModel(AbstractModel):
    """Model for garbage strings indicators
    """

    def __init__(self, app_config):
        super(IndicatorModel, self).__init__(app_config)

        self.model = {
            "strong": StrongIndicatorList(),
            "clean": CleanIndicatorList()
        }

    def load(self, text_data):
        for indicator_list in self.model.values():
            indicator_list.set_stats(text_data.stats)

    def correct(self, text_data):
        # =======================
        # Strong indicators
        # =======================
        lines = [line for paragraph in text_data.text for line in paragraph
                 if line.grade != 0 and self.model["strong"].match(line)]

        for line in lines:
            line.set_garbage()

        # =======================
        # Clean indicators
        # =======================
        lines = [line for paragraph in text_data.text for line in paragraph
                 if line.grade != 0 and self.model["clean"].match(line)]

        for line in lines:
            line.set_clean()

        # =======================
        # Post processing
        # =======================
        lines = [line for paragraph in text_data.text for line in paragraph]
        previous_line = None

        # Smoothing function
        for line in lines:
            # Decrease grade if previous line is a garbage string
            if previous_line is not None and previous_line.grade == 0 and line.grade != 5:
                line.decrease_grade()

            # Decrease grade of previous line
            if line.grade == 0 and previous_line is not None and previous_line.grade != 5:
                previous_line.decrease_grade()

            previous_line = line


class MachineLearningModel(AbstractModel):
    """Model storing all machine learning data
    """

    def __init__(self, app_config):
        super(MachineLearningModel, self).__init__(app_config)

        self.model = {
            "algo": MachineLearningAlgorithm(),
            "features": MachineLearningFeatures()
        }

    def train(self, dataset):
        # Get the original training set
        training_set = self.model["algo"].training_set

        # Append the new data to it
        for text in dataset:
            self.logger.debug("Processing "+text.filename+"...")
            unigrams = Unigrams(join(self.config["root"],
                                     self.config["dirs"]["models_root"],
                                     self.config["dirs"]["models"]["inline"],
                                     self.config["models"]["inline"]["unigrams"],))

            for p in text.text:
                for line in p:
                    if line.grade % 5 != 0:  # Unclassified lines are useless for the training
                        continue

                    f = MachineLearningFeatures()
                    features = f.extract_features(line, unigrams.ngrams, text.stats)
                    result = int(line.grade / 5)

                    training_set["features"].append(features)
                    training_set["results"].append(result)

        self.logger.debug("Saving training set...")
        save(training_set, join(self.config["dirs"]["models_root"],
                                self.config["dirs"]["models"]["learning"],
                                self.config["models"]["learning"]["training_set"]))

        self.logger.debug("Training model...")
        ml_classifier = SGDClassifier(loss="log", class_weight="auto")
        self.model["algo"].set_classifier(ml_classifier)
        self.model["algo"].set_training_set(training_set["features"], training_set["results"])
        self.model["algo"].train()

        save(self.model["algo"].classifier, join(self.config["dirs"]["models_root"],
                                                 self.config["dirs"]["models"]["learning"],
                                                 self.config["models"]["learning"]["classifier"]))

    def load(self, text_data):
        pass

    def correct(self, text_data):
        unigrams = Unigrams(join(self.config["root"],
                                 self.config["dirs"]["models_root"],
                                 self.config["dirs"]["models"]["inline"],
                                 self.config["models"]["inline"]["unigrams"],))

        ml_classifier = load(join(self.config["dirs"]["models_root"],
                                  self.config["dirs"]["models"]["learning"],
                                  self.config["models"]["learning"]["classifier"]))

        if ml_classifier is None:
            return

        self.model["algo"].set_classifier(ml_classifier)

        for paragraph in text_data.text:
            for line in paragraph:
                if line.grade % 5 == 0:
                    continue

                f = MachineLearningFeatures()
                features = f.extract_features(line, unigrams.ngrams, text_data.stats)
                line.grade = self.model["algo"].classify(features) * 5