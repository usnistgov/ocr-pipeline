"""Utilitaries for inline denoising
"""
from hashlib import md5
from collections import Counter
from copy import deepcopy
from math import log
from operator import add
from nltk.metrics.distance import edit_distance
import operator
from denoiser.models.inline.hashing import anagram_hash, ocr_key_hash
from denoiser.models.inline.ranking import rate_anagram, rate_ocr_key, rate_bigram


def init_correction_map(token, dictionary):
    """Initialize the correction dictionary

    Parameters:
        token (:func:`str`): Cleaned token
        dictionary (:func:`dict`): Dictionary structure

    Returns:
        :func:`dict` or :data:`None` - Correction map
    """
    if token is None:
        return None

    if len(token) <= 2 or token.lower() in dictionary:
        return {token: 1}

    return {}


def generate_alphabet_from_word(word):
    """Generate anagram hash for all chars in a word

    Parameters:
        word (:func:`str`): Word to generate hash
    Returns:
        set - Set of hashes
    """
    word = " "+word+" "
    chars = [char for char in word]  # Getting letters from the word
    chars += map(add, chars[:-1], chars[1:])  # Adding bigrams to the list

    # Computing hash of items and add 0 to the list
    return set([0] + [anagram_hash(c) for c in set(chars)])


def select_anagrams(token, structures):
    """Select possible anagrams for a given token

    Parameters:
        token (:func:`str`): Cleaned token
        structures (:func:`dict`): Datastructures from file

    Returns:
        :func:`dict` - Possible anagrams (keys) along with their score (values)
    """
    anagrams = {}
    focus_alphabet = generate_alphabet_from_word(token[1])
    token_hash = anagram_hash(token)

    hash_list = []
    for c in structures["alphabet"]:
        for f in focus_alphabet:
            hash_list.append(token_hash + c - f)

    hash_counter = Counter(hash_list)  # Counting retrieval occurence

    for h in set(hash_counter.keys()).intersection(set(structures["anagrams"].keys())):
        count = hash_counter[h]
        anag_list = [anag for anag in structures["anagrams"][h] if edit_distance(anag, token) <= 3]

        for anag in anag_list:
            anag_score = rate_anagram(structures["occurence_map"], token, anag, count)

            if anag_score > 0:
                anagrams[anag] = anag_score

    return anagrams


def select_ocrsims(token, structures):
    """Select similar words for a given token

    Parameters:
        token (:func:`str`): Cleaned token
        structures (:func:`dict`): Datastructures from file

    Returns:
        :func:`dict` - Similar words (keys) along with their score (values)
    """
    delta = 2
    ocr_sims = {}

    word_hash = ocr_key_hash(token)

    sim_hash_list = {}  # Using a dictionary avoid multiple entries if a key is retrieved twice
    key_index = -1

    # for (key, value) in word_hash:
    for key, value in word_hash:
        key_index += 1
        sim_hash = deepcopy(word_hash)

        for d in range(-delta, delta+1):
            if d != 0:
                card = max(int(value)+d, 1)

                sim_hash[key_index] = (key, card)

                # Rebuild OCR key string
                sim_hash_str = ""
                for k, v in sim_hash:
                    sim_hash_str += k + str(v)

                if sim_hash_str in structures["ocrkeys"]:
                    card_diff = abs(int(value)-card)

                    sim_hash_list[sim_hash_str] = [(sim_word, card_diff)
                                                   for sim_word in structures["ocrkeys"][sim_hash_str]
                                                   if edit_distance(sim_word, token) <= 2]

    for sim_hash_str, sim_list in sim_hash_list.items():
        for sim_word, card_diff in sim_list:
            sim_score = rate_ocr_key(structures["occurence_map"], token, sim_word, card_diff)

            if sim_score > 0:
                ocr_sims[sim_word] = sim_score

    return ocr_sims


def truncate_ocr_sim_list(token, ocr_sims_list, limit=10):
    """Truncate the OCR key similarity list to a defined set of possibilities

    Parameters:
        token (:func:`str`): Initial token
        ocr_sims_list (list): OCR similarities
        limit (int): Final number of similarities

    Returns:
        list - List of similarities to keep
    """
    if len(ocr_sims_list) <= limit:
        return ocr_sims_list

    ocr_scores = set([sc for sim, sc in ocr_sims_list.items()])

    # Limit of 10 different scores allowed
    sorted_ocr_scores = sorted(ocr_scores, reverse=True)[:limit]
    ocr_list = []
    for score in sorted_ocr_scores:
        tmp_ocr_list = [ocr_sims for ocr_sims, ocr_score in ocr_sims_list.items() if ocr_score == score]

        if len(ocr_list) + len(tmp_ocr_list) > limit:
            list_len = limit - len(ocr_list)
            tmp_list = []

            while len(tmp_list) < list_len:
                tmp_list += select_lower_edit_distance(token, tmp_ocr_list)

            if len(ocr_list) + len(tmp_list) == limit:  # Final list has exactly 10 elements
                ocr_list += tmp_list
                break
            else:  # List has more than 10 arguments (need to chose only the n elements needed)
                alpha_tmp_list = []

                while len(alpha_tmp_list) != list_len:
                    alpha_word = select_best_alphabetical_word(token, tmp_list)

                    alpha_tmp_list.append(alpha_word)
                    tmp_list = [tkn for tkn in tmp_list if tkn != alpha_word]

                ocr_list += alpha_tmp_list
                break
        elif len(ocr_list) + len(tmp_ocr_list) == limit:
            ocr_list += tmp_ocr_list
            break
        else:  # len(ocr_list) + len(tmp_ocr_list) < limit
            ocr_list += tmp_ocr_list

    if len(ocr_list) != limit:
        raise IndexError("OCR list is still too big ("+str(len(ocr_list))+"/"+str(limit)+")")

    return {tkn: ocr_sims_list[tkn] for tkn in ocr_list}


def split_ocr_list(token, ocr_list):
    """Split the OCR list between strong and week OCR words

    Parameters:
        token (:func:`str`): Token to correct
        ocr_list (list): List of possible OCR correction
    Returns:
        tuple - Strong OCR words and weak OCR words
    """

    # Build the sorted OCR key list and divide it into 2 different stacks
    ocr_words = sorted(
        ocr_list.iteritems(),
        key=operator.itemgetter(1),
        reverse=True
    )
    strong_ocr_words = {tkn: sc for tkn, sc in ocr_words[:5]}
    weak_ocr_words = {tkn: sc for tkn, sc in ocr_words[5:]}

    min_strong_score = min([sc for tkn, sc in strong_ocr_words.items()])
    max_weak_score = max([sc for tkn, sc in weak_ocr_words.items()])

    if min_strong_score == max_weak_score:
        strong_tmp_ocr_words = [tkn for tkn, score in strong_ocr_words.items() if score == min_strong_score]
        weak_tmp_ocr_words = [tkn for tkn, score in weak_ocr_words.items() if score == min_strong_score]

        tmp_list = {t: min_strong_score for t in strong_tmp_ocr_words}
        tmp_list.update({t: min_strong_score for t in weak_tmp_ocr_words})

        tmp_strg_list = truncate_ocr_sim_list(token, tmp_list, len(strong_tmp_ocr_words))
        tmp_weak_list = [tkn for tkn in tmp_list.keys() if tkn not in tmp_strg_list]

        strong_ocr_words = {tkn: sc for tkn, sc in strong_ocr_words.items() if tkn not in tmp_list.keys()}
        strong_ocr_words.update(tmp_strg_list)

        weak_ocr_words = {tkn: sc for tkn, sc in weak_ocr_words.items() if tkn not in tmp_list.keys()}
        weak_ocr_words.update({tkn: min_strong_score for tkn in tmp_weak_list})

    return strong_ocr_words, weak_ocr_words


def build_candidates_list(token, anagrams_list, ocr_sims_list, structures):
    """Merge anagram and OCRkey list into one list.

    Parameters:
        token (:func:`str`): Cleaned token
        anagrams_list (:func:`dict`): Result of `select_anagrams`
        ocr_sims_list (:func:`dict`): Result of `select_ocrsims`
        structures (:func:`dict`): Datastructures from file

    Returns:
        :func:`dict` - Correction tokens (keys) along with their score (values)
    """
    final_list = anagrams_list

    ocr_list = truncate_ocr_sim_list(token, ocr_sims_list)

    strong_ocr_list = ocr_list
    weak_ocr_list = {}
    if len(ocr_list) > 5:
        (strong_ocr_list, weak_ocr_list) = split_ocr_list(token, ocr_list)

    for ocr_word, ocr_score in strong_ocr_list.items():
        if ocr_word in final_list.keys():
            final_list[ocr_word] *= ocr_score
            del strong_ocr_list[ocr_word]

    strong_ocr_list.update(weak_ocr_list)

    for ocr_word, ocr_score in strong_ocr_list.items():
        if ocr_word not in final_list.keys():
            final_list[ocr_word] = rate_anagram(structures["occurence_map"], token, ocr_word, 1) \
                * rate_ocr_key(structures["occurence_map"], token, ocr_word, 0)

    return final_list


def find_correct_case(word, case_mode, structures):
    """Select the best case between a set of already encountered cases

    Parameters:
        word (:func:`str`): Word to correct
        case_mode (int): Choice between lower or upper case (extra choice for undecisive)
        structures (list): List of structures needed to perform the choice
    Returns:
        :func:`str` - Corrected word
    """
    variations = {key: structures["occurence_map"][key] for key in structures["altcase"][word.lower()]}
    variations = sorted(variations.iteritems(), key=operator.itemgetter(1), reverse=True)

    tmp_vars = []
    if case_mode == 0:  # Upper case spelling
        for var in variations:
            _word = var[0]
            if _word[0].isupper() and sum(char.isupper() for char in _word) > 2:
                tmp_vars.append(var)

        if len(tmp_vars) == 0:
            tmp_vars = variations
    elif case_mode == 1:  # Lower case with capital initial
        for var in variations:
            _word = var[0]
            if _word[0].isupper() and sum(char.isupper() for char in _word) <= 2:
                tmp_vars.append(var)

        if len(tmp_vars) == 0:
            tmp_vars = variations
    else:  # case_mode == -1 (no capital letters found)
        tmp_vars = variations

    max_occ = tmp_vars[0][1]
    dist_vars = {term: edit_distance(word, term) for term, occ in tmp_vars if occ == max_occ}

    if len(dist_vars) == 1:
        return dist_vars.keys()[0]

    # Several terms with max occurence still exist
    dist_vars = sorted(dist_vars.iteritems(), key=operator.itemgetter(1))

    min_dist = dist_vars[0][1]
    min_dist_vars = [term for term, dist in dist_vars if dist == min_dist]

    if len(min_dist_vars) == 1:
        return min_dist_vars[0]

    # Several terms with same Levenhstein distance exist
    term_ascii_code = {term: [ord(ch) for ch in term] for term in min_dist_vars}

    for ascii_code in term_ascii_code.values():
        for i in xrange(len(ascii_code)):
            code = ascii_code[i]

            # Non a-zA-Z chars will have a 0 value
            if code < 65 or 90 < code < 97 or code > 122:
                ascii_code[i] = 0

    if case_mode >= 0:
        ascii_val = min(term_ascii_code.values())

        t = [t for t, v in term_ascii_code.items() if v == ascii_val]

        if len(t) > 1:
            raise ValueError("Too many value in final array")

        return t[0]
    else:
        ascii_val = max(term_ascii_code.values())

        t = [t for t, v in term_ascii_code.items() if v == ascii_val]

        if len(t) > 1:
            raise ValueError("Too many value in final array")

        return t[0]


def correct_case(token, corrections_map, structures):
    """Select the best spelling for a word (case-wise)

    Parameters:
        token (:func:`str`): Cleaned token
        correction_map (:func:`dict`): Result of `build_candidates_list`
        structures (:func:`dict`): Datastructures from file

    Returns:
        :func:`dict` - Corrected tokens (keys) along with their score (values)
    """
    alt_case_mode = -1  # Most common variation
    if token[0].isupper():
        if sum(char.isupper() for char in token) > 2:
            alt_case_mode = 0  # Upper case variation
        else:
            alt_case_mode = 1  # Lower case variation with capital first letter

    corrected_case_map = {}
    for correct_word, score in corrections_map.items():
        if correct_word.find(" ") != -1:
            words = correct_word.split(" ")

            keys_left = find_correct_case(words[0], alt_case_mode, structures)
            keys_right = find_correct_case(words[1], alt_case_mode, structures)
            key = keys_left+" "+keys_right
        else:
            key = find_correct_case(correct_word, alt_case_mode, structures)

        # If the key already exists we keep the highest score
        if key in corrected_case_map.keys():
            old_score = corrected_case_map[key]
            corrected_case_map[key] = max(old_score, score)
        else:
            corrected_case_map[key] = score

    return corrected_case_map


def apply_bigram_boost(paragraph, bigrams, occurence_map):
    """Compute the bigram boost for every token of a paragraph and apply it to the possible corrections.

    Parameters:
        paragraph (:func:`list`): List of lines
        bigrams (:func:`list`): Bigrams for the given paragraph
        occurence_map (:func:`dict`): Occurence of unigrams and bigrams
    """
    token_index = -1

    for line in paragraph:
        for token in line.tokens:
            if token[2] is None:
                continue

            # Finding adjacent tokens
            adjacent_tokens = []

            if token_index > 0:
                adjacent_tokens.append(bigrams[token_index][0])
            else:
                adjacent_tokens.append(None)

            token_index += 1

            if token_index < len(bigrams):
                adjacent_tokens.append(bigrams[token_index][1])
            else:
                adjacent_tokens.append(None)

            # Normalizing adjacent tokens array
            for tkn_index in xrange(len(adjacent_tokens)):
                adj_tkn = adjacent_tokens[tkn_index]

                if adj_tkn is None:
                    adjacent_tokens[tkn_index] = []
                    continue

                if not adj_tkn[2] is None:
                    adjacent_tokens[tkn_index] = []
                    adj_tkn = sorted(adj_tkn[2].iteritems(), key=operator.itemgetter(1), reverse=True)

                    for idx in xrange(min(5, len(adj_tkn))):
                        adjacent_tokens[tkn_index].append(adj_tkn[idx][0].lower())
                else:
                    if not adj_tkn[1] is None:
                        adjacent_tokens[tkn_index] = [adj_tkn[1].lower()]
                    else:
                        adjacent_tokens[tkn_index] = [adj_tkn[0].lower()]

            # Computing bigram boost
            for correction in token[2].keys():
                bigram_boost = rate_bigram(correction.lower(), adjacent_tokens[0], adjacent_tokens[1], occurence_map)
                token[2][correction] *= bigram_boost


def select_lower_edit_distance(ref_word, word_list):
    """Get the word with the lower edit distance

    Parameters:
        ref_word (:func:`str`): Word to correct
        word_list (list): List of proposals
    
    Returns:
        :func:`str` - Selected word
    """
    word_dict = {word: edit_distance(ref_word, word) for word in word_list}
    min_dist = min(word_dict.values())

    return [word for word, dist in word_dict.items() if dist == min_dist]


def select_by_hash(word_list):
    """Select the word with the lower md5 hash

    Parameters:
        word_list (list): List of proposal

    Returns:
        :func:`str` - Selected word
    """
    hashes = set([md5(word).hexdigest() for word in word_list])

    if len(hashes) != len(word_list):
        raise Exception("differenciation impossible")

    return [tkn for tkn in word_list if md5(tkn).hexdigest() == min(hashes)][0]


def select_best_alphabetical_word(ref_word, word_list):
    """Select closest alphabetical word (non alphanumerical chars are set to the same value)

    Parameters:
        ref_word (:func:`str`): Word to correct
        word_list (list): List of propositions

    Returns:
        :func:`str` - Selected word
    """
    case_mode = -1 if ref_word[0].isupper() else 0
    term_ascii_code = {term: [ord(ch) for ch in term] for term in word_list}

    for ascii_code in term_ascii_code.values():
        for i in xrange(len(ascii_code)):
            code = ascii_code[i]

            # Non a-zA-Z chars will have a 0 value
            if code < 65 or 90 < code < 97 or code > 122:
                ascii_code[i] = 0

    if case_mode >= 0:
        ascii_val = min(term_ascii_code.values())

        tkn_list = [t for t, v in term_ascii_code.items() if v == ascii_val]

        if len(tkn_list) > 1:
            return select_by_hash(tkn_list)

        return tkn_list[0]
    else:
        ascii_val = max(term_ascii_code.values())

        tkn_list = [t for t, v in term_ascii_code.items() if v == ascii_val]

        if len(tkn_list) > 1:
            return select_by_hash(tkn_list)

        return tkn_list[0]


def select_correction(word, corrections_map):
    """Select the best correction for a word given its score

    Parameters:
        corrections_map (:func:`dict`): Dictionary containing all corrections for a token along with their score

    Returns:
        :func:`dict` - Chosen correction(s) along with their score
    """
    if corrections_map is None or len(corrections_map) == 1:
        return corrections_map

    max_val = max(corrections_map.values())
    final_list = {term: val for term, val in corrections_map.items() if val == max_val}

    if len(final_list) == 1:  # One value has the maximum
        if final_list.values()[0] > 0.7:  # Highly valued terms are chosen by default
            return final_list

        first_word = final_list.keys()[0]

        # If the threshold value has not been reached we are looking for a second term
        del corrections_map[final_list.keys()[0]]

        max_val = max(corrections_map.values())
        tmp_list = {term: val for term, val in corrections_map.items() if val == max_val}

        if len(tmp_list) == 1:  # One value has the second higher grade
            final_list.update(tmp_list)
            second_word = tmp_list.keys()[0]
        else:  # Several terms with the same score
            # Differenciation on the Levenhstein distance
            tmp_list = select_lower_edit_distance(word, tmp_list.keys())

            if len(tmp_list) == 1:  # One term has the lowest score
                final_list[tmp_list[0]] = max_val
                second_word = tmp_list[0]
            else:  # Several terms with the same
                # Choose the best alphabetical term
                second_word = select_best_alphabetical_word(word, tmp_list)
                final_list[second_word] = max_val

        # Determine if we need one or two terms
        if log(final_list[first_word] / final_list[second_word]) >= 1:
            del final_list[second_word]

        return final_list
    elif len(final_list) != 2:  # More than 2 values share the same maximum
        tmp_list = select_lower_edit_distance(word, final_list.keys())

        if len(tmp_list) == 1:  # One word get the min edit distance
            first_word = tmp_list[0]
            tmp_final_list = final_list
            del tmp_final_list[first_word]

            tmp_list = select_lower_edit_distance(word, tmp_final_list.keys())

            if len(tmp_list) == 1:  # One word get the second minimal edit distance
                final_list = {
                    first_word: max_val,
                    tmp_list[0]: max_val
                }

                return final_list
            else:  # The second minimal edit distance is shared by several terms
                best_term = select_best_alphabetical_word(word, tmp_list)

                final_list = {
                    first_word: max_val,
                    best_term: max_val
                }

                return final_list
        elif len(tmp_list) == 2:  # Exactly two word get the same min edit distance
            final_list = {
                tmp_list[0]: max_val,
                tmp_list[1]: max_val
            }

            return final_list
        else:  #
            best_term_1 = select_best_alphabetical_word(word, tmp_list)

            tmp_list = [term for term in tmp_list if term != best_term_1]
            best_term_2 = select_best_alphabetical_word(word, tmp_list)

            final_list = {
                best_term_1: max_val,
                best_term_2: max_val
            }

            return final_list
    else:  # Two words with the same score
        return final_list


def extract_paragraph_bigrams(paragraph):
    """Get bigrams for a given paragraph

    Parameters:
        paragraph (list): Paragraph to extract bigrams from

    Returns:
        list - Bigram list
    """
    p_tokens = [token for line in paragraph for token in line.tokens]
    bigram_list = []

    for index in xrange(len(p_tokens) - 1):
        bigram_list.append((p_tokens[index], p_tokens[index + 1]))

    return bigram_list