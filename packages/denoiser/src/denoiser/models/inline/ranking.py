"""Ranking functions used across the denoiser
"""
from math import log
from nltk.metrics.distance import edit_distance


def rate_anagram(freq_map, word, anagram, int_retrievals):
    """Rate an anagram

    Parameters:
        freq_map (dict): Occurence map
        word (:func:`str`): Word to evaluate
        anagram (:func:`str`): Possible anagram
        int_retrievals (int): Internal retrievals

    Returns:
        float: OCR key score
    """
    score = len(word) - edit_distance(word, anagram)
    score *= int_retrievals * log(freq_map[anagram.lower()])

    return score


def rate_ocr_key(freq_map, word, ocr_sim, cardinality):
    """Rate an OCR key

    Parameters:
        freq_map (dict): Occurence map
        word (:func:`str`): Word to evaluate
        ocr_sim (:func:`str`): Possible OCR key
        cardinality (int): Cardinality

    Returns:
        float: OCR key score
    """
    score = len(word) - edit_distance(word, ocr_sim) - cardinality
    score *= log(freq_map[ocr_sim.lower()])

    return score


def rate_bigram(correction, previous_tokens, next_tokens, occurence_map):
    """Get the bigram boost of a given token

    Parameters:
        correction (:func:`str`): Correction word to evaluate
        previous_tokens (list): Possible previous tokens
        next_tokens (list): Possible next tokens
        occurence_map (dict): Occurence map

    Returns:
        float: Bigram score
    """
    min_score = 2
    total_score = 0

    bigrams = [previous_w+" "+correction for previous_w in previous_tokens] + \
              [correction+" "+next_w for next_w in next_tokens]

    for bigram in bigrams:
        total_score += occurence_map[bigram]

    return log(max(min_score, total_score))


def rate_corrections(correction_list):
    """Bring the score between 0 and 1

    Parameters:
        correction_list (list): The list of correction
    Returns:
        list: Correction list with corrected scores
    """
    if len(correction_list) == 1:
        key = correction_list.keys()[0]
        correction_list[key] = 1

        return correction_list

    total_score = sum(correction_list.values())

    return {correction: score/total_score for correction, score in correction_list.items()}
