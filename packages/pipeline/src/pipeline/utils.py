"""Main utility package
"""
from hashlib import sha256
from os import makedirs
from os.path import join
from shutil import move

local_config = {
    "tmp_dir": "tmp",
    "dirs": ["png", "txt/segments"]
}


def create_data_directory(filename):
    """Create the data directory for a PDF file

    Parameters:
        filename (:func:`str`):

    Returns:
        :func:`str`  - Location of the directory
    """
    if not filename.endswith(".pdf"):
        return None

    file_hash = sha256(open(filename).read()).hexdigest()
    tmp_dir = join(local_config["tmp_dir"], file_hash)

    # Creating main directory with the PDF inside
    makedirs(tmp_dir)
    move(filename, tmp_dir)

    # Creating subdirectories
    for subdir in local_config["dirs"]:
        makedirs(join(tmp_dir, subdir))

    return tmp_dir