"""File operations packages. Provide functions to interact with the filesystem.

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
from zipfile import ZipFile
from os import walk, remove, makedirs
from os.path import join, splitext, exists
from shutil import rmtree
from hashlib import sha256

module_conf = {
    "zip_ext": ".zip"
}


def zip_directory(directory):
    """Zip a directory

    Parameters:
        directory (str): Path to the directory to zip.

    Returns:
        str: Path to the archive.
    """
    archive_name = directory + module_conf["zip_ext"]
    zip_dir = ZipFile(archive_name, "w")

    for root, folders, files in walk(directory):
        for item in folders+files:
            orig_path = join(root, item)
            dest_path = orig_path[len(directory):]

            zip_dir.write(orig_path, dest_path)

    rmtree(directory)  # Clean directory
    return archive_name


def unzip_directory(archive):
    """Unzip an archive.

    Parameters:
        archive (str): Path to the archive to unzip.

    Returns:
        str: Path to the directory.
    """
    zip_dir = ZipFile(archive, "r")
    directory = splitext(archive)[0]

    zip_dir.extractall(directory)
    remove(archive)

    return directory


def create_directories(dir_conf, prefix=None):
    """Create application directories and subdirectories given a configuration dictionary.

    Parameters:
        dir_conf (dict): List of directories to create.
        prefix (str): Root directory for the directories to create. Default to `None` (directories will be built in
            the current directory).

    Raises:
        ValueError: If there is a subdirectory with no root or if the subdirectory key is not a dictionary.
    """
    dirnames = [d for d in dir_conf.values() if isinstance(d, str)]

    for dirname in dirnames:
        dirpath = join(prefix, dirname) if prefix is not None else dirname

        if not exists(dirpath):
            makedirs(dirpath)

    dir_keys = dir_conf.keys()
    roots = [d for d in dir_keys if d.endswith("_root") and d.split("_root")[0] in dir_keys]
    dir_dicts = [d for d in dir_conf.values() if not isinstance(d, str)]

    # More dictionaries than roots
    if len(roots) < len(dir_dicts):
        raise TypeError("All subdirectory must have a _root key")

    for r in roots:
        key = r.split("_root")[0]
        subfolders = dir_conf[key]

        if not isinstance(subfolders, dict):
            raise TypeError("Expecting dict, got "+str(type(subfolders)))

        if prefix is not None:
            prefix = join(prefix, dir_conf[r])
        else:
            prefix = dir_conf[r]

        create_directories(subfolders, prefix)


def file_checksum(filename):
    """Return the sha256 digest of a file.

    Parameters:
        filename (str): The file to hash.

    Returns:
        str: Hash of the file.
    """
    return sha256(open(filename).read()).hexdigest()

