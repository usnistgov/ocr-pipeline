"""Package containing all the machine learning functions and objects

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
import logging
from numpy import mean
from numpy.lib.polynomial import poly1d


logger = logging.getLogger("app")


class MachineLearningAlgorithm(object):
    """Machine learning algorithm
    """

    def __init__(self):
        self.training_set = {
            "features": [],
            "results": []
        }

        self.classifier = None

        logger.info("Model created (new)")

    def set_classifier(self, cls):
        self.classifier = cls
        logger.info(cls.__class__.__name__+" model loaded")

    def set_training_set(self, features, results):
        if len(features) != len(results):
            raise AttributeError("Number of features and result are different")

        self.training_set["features"] = features
        self.training_set["results"] = results

        logger.debug("Training set uploaded")

    def train(self):
        self.classifier.fit(self.training_set["features"], self.training_set["results"])
        logger.debug("Model trained")

    def classify(self, features):
        return self.classifier.predict(features)

    def compute_error(self, features, results):
        prediction = self.classifier.predict(features)
        error = 0

        for index in xrange(len(prediction)):
            if results[index] < 0:
                continue

            error += ((prediction[index] - results[index]) / 5)**2

        error /= (2*len(prediction))
        return error


class MachineLearningFeatures(object):
    """Feature calculator for machine learning
    """

    def __init__(self):
        self.features = []

    def extract_features(self, line, unigrams, text_stats):
        # Simple features
        features = [
            float(line.stats["orig"].get_stat("lw_char")),
            float(line.stats["orig"].get_stat("up_char")),
            float(line.stats["orig"].get_stat("sp_char")),
            float(line.stats["orig"].get_stat("nb_char")),
            float(len(line.tokens)),
        ]

        # Additional features
        fappend = features.append
        fappend(line.get_clean_stats().get_stat("lw_char"))
        fappend(line.get_clean_stats().get_stat("up_char"))
        fappend(line.get_clean_stats().get_stat("sp_char"))
        fappend(line.get_clean_stats().get_stat("nb_char"))
        fappend(line.get_line_score())
        fappend(len(line.get_orig_line()))
        fappend(len(line.get_clean_line()))

        u = unigrams

        tk_len = [len(token[0]) for token in line.tokens]
        word_avg_len = 0

        if len(tk_len) > 0:
            word_avg_len = mean(tk_len)

        fappend(float(word_avg_len))

        t0 = [u[tk[0]] for tk in line.tokens]
        s0 = 0

        if len(t0) != 0:
            s0 = mean(t0)

        fappend(float(s0))

        t1 = [u[tk[1]] for tk in line.tokens if not tk[1] is None]
        s1 = 0

        if len(t1) != 0:
            s1 = mean(t1)

        fappend(float(s1))

        t2 = [u[t] for tk in line.tokens if not tk[2] is None for t in tk[2].keys()]
        s2 = 0

        if len(t2) != 0:
            s2 = mean(t2)

        fappend(float(s2))

        # Regularization
        orig_chars = sum(features[:4])
        clean_chars = sum(features[5:9])

        f = [
            features[0] / orig_chars,
            features[1] / orig_chars,
            features[2] / orig_chars,
            features[3] / orig_chars
        ]

        if clean_chars != 0:
            f += [features[5] / clean_chars,
                  features[6] / clean_chars,
                  features[7] / clean_chars,
                  features[8] / clean_chars]
        else:
            f += [0, 0, 0, 0]

        f += [features[9],
              features[4] / text_stats.get_stat("word_avg_nb"),
              features[12] / text_stats.get_stat("word_avg_length"),
              features[10] / text_stats.get_stat("line_avg_length"),
              features[11] / text_stats.get_stat("line_avg_length")]

        if features[13] != 0:
            f.append(features[14] / features[13])
            f.append(features[15] / features[13])
        else:
            f.append(0)
            f.append(0)

        features = f

        # Ordering the data set
        features = [
            features[11],  # Original line average len
            features[12],  # Clean line average len
            features[9],  # Original line average len
            features[10],  # Clean line average len
            features[13],  # Original line average len
            features[14],  # Clean line average len
            features[0],  # Original line average len
            features[1],  # Clean line average len
            features[2],  # Original line average len
            features[3],  # Clean line average len
            features[4],  # Original line average len
            features[5],  # Clean line average len
            features[6],  # Original line average len
            features[7],  # Clean line average len
        ]

        # Polynomial features
        degree = 1
        poly_feat = []
        p_feat = poly1d(features)

        for d in xrange(degree):
            poly_feat += (p_feat ** (d+1)).coeffs.tolist()

        del poly_feat[5]

        self.features = poly_feat

        return self.features
