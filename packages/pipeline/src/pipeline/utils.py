"""Main utility package

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
from hashlib import sha256
from os import makedirs
from os.path import join
from random import choice
from shutil import move
from string import ascii_lowercase, digits
from time import strftime, gmtime

local_config = {
    "tmp_dir": "tmp",  # FIXME not used anymore
    "dirs": ["png", "txt/segments"]
}


def create_data_directory(filename, tmp_dir):
    """Create the data directory for a PDF file

    Parameters:
        filename (:func:`str`):
        tmp_dir (str):

    Returns:
        :func:`str`  - Location of the directory
    """
    if not filename.endswith(".pdf"):
        return None

    # Generate a unique directory name
    file_hash = sha256(open(filename).read()).hexdigest()[0:12]
    creation_time = strftime("%Y%m%d.%H%M%S", gmtime())
    rand_str = ''.join(choice(ascii_lowercase + digits) for _ in range(6))

    tmp_dir = join(tmp_dir, "%s.%s.%s" % (file_hash, creation_time, rand_str))

    # Creating main directory with the PDF inside
    makedirs(tmp_dir)
    move(filename, tmp_dir)

    # Creating subdirectories
    for subdir in local_config["dirs"]:
        makedirs(join(tmp_dir, subdir))

    return tmp_dir
