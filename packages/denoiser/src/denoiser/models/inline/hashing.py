"""Hashing functions use for anagrams and ocr keys

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

ocr_key_class_map = {
    # Lower case
    "a": ("o", 1), "b": ("o", 1), "c": ("c", 1), "d": ("o", 1), "e": ("c", 1), "f": ("i", 1),
    "g": ("o", 1), "h": ("i", 2), "i": ("i", 1), "j": ("i", 1), "k": ("i", 1), "l": ("i", 1),
    "m": ("i", 3), "n": ("i", 2), "o": ("o", 1), "p": ("o", 1), "q": ("o", 1), "r": ("i", 1),
    "s": ("s", 1), "t": ("i", 1), "u": ("i", 2), "v": ("v", 1), "w": ("v", 2), "x": ("v", 1),
    "y": ("v", 1), "z": ("z", 1),

    # Upper case
    "A": ("a", 1), "B": ("i", 1), "C": ("c", 1), "D": ("i", 1), "E": ("i", 1), "F": ("i", 1),
    "G": ("c", 1), "H": ("i", 2), "I": ("i", 1), "J": ("i", 1), "K": ("i", 1), "L": ("i", 1),
    "M": ("i", 3), "N": ("i", 2), "O": ("o", 1), "P": ("i", 1), "Q": ("o", 1), "R": ("i", 1),
    "S": ("s", 1), "T": ("i", 1), "U": ("i", 2), "V": ("v", 1), "W": ("v", 2), "X": ("v", 1),
    "Y": ("v", 1), "Z": ("z", 1),

    # Numbers and special chars
    "0": ("o", 1), "1": ("i", 1), "5": ("s", 1), "6": ("o", 1), "9": ("o", 1), "!": ("i", 1),
    "'": ("'", 1), "-": ("-", 1)
}


def anagram_hash(word):
    """Compute anagram hash of a word

    Parameters:
        word (:func:`str`): Word that needs to be hashed

    Returns:
        int: Anagram representation of the word
    """
    anag_hash = sum([pow(ord(char), 5) for char in word])

    return anag_hash


def ocr_key_hash(word):
    """Generate OCR key hash from a word

    Parameters:
        word (:func:`str`): Word that needs to be hashed

    Returns:
        list: OCR key hash of the word
    """
    ocrk_hash = []

    for char in word:
        if char not in ocr_key_class_map:
            char_class = ("#", 1)
        else:
            char_class = ocr_key_class_map[char]

        if len(ocrk_hash) > 0 and ocrk_hash[-1][0] == char_class[0]:
            ocrk_hash[-1] = (char_class[0], ocrk_hash[-1][1] + char_class[1])
        else:
            ocrk_hash.append(char_class)

    return ocrk_hash


def ocr_key_list_to_str(ocr_key_list):
    """Generate OCR key string from the list

    Parameters:
        ocr_key_list (list): OCR key hash of a word

    Returns:
        :func:`str`: OCR key string
    """
    ocr_key_str = ""

    for key_tuple in ocr_key_list:
        ocr_key_str += key_tuple[0] + str(key_tuple[1])

    return ocr_key_str
