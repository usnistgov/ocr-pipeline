"""Configuration package. Contains some functions to access YAML configuration file.

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
import logging.config
from os import makedirs
from os.path import exists, join, isfile, splitext, dirname
import yaml

app_config = None


def load_config(filename, root_directory):
    """Load a YAML configuration file. All data is stored in :attr:`denoiser.app_config`.

    Parameters:
        filename (:func:`str`): YAML configuration file
    """
    global app_config

    with open(filename, "r") as conf_file:
        app_config = yaml.load(conf_file)

    install_dir = dirname(filename)

    # Logging configuration
    if "log_conf" in app_config.keys():
        log_conf_name = join(install_dir, app_config["log_conf"])
        with open(log_conf_name, "r") as log_conf_file:
            log_conf = yaml.load(log_conf_file)

            # Create logs directory if it does not exist
            log_directory = join(root_directory, app_config["dirs"]["logs"])
            if not exists(log_directory):
                makedirs(log_directory)

            # Append the log folder to the log filename
            for handler in log_conf["handlers"].values():
                if "filename" in handler.keys():
                    handler["filename"] = join(log_directory, handler["filename"])

            logging.config.dictConfig(log_conf)

        del app_config["log_conf"]  # Information is no longer needed

    # Import other YAML configuration file
    for key, value in app_config.items():
        if type(value) == str and isfile(join(install_dir, value)) and splitext(value)[1] == ".yaml":
            with open(join(install_dir, value), "r") as subconf_file:
                app_config[key] = yaml.load(subconf_file)


def get_config(key):
    """Return value of a given key hash. Subelement are split using '/'. Access to list element is done using '#'.

    Parameters:
        key (:func:`str`): Key hash to find

    Returns:
        :func:`str`: Value for the given key

    Raises:
        ValueError: App config has not been loaded
        KeyError: Key hash has not been found
    """
    if app_config is None:
        raise ValueError("App config not loaded")

    try:
        if '/' in key:
            keys = key.split('/')

            tmp_keys = []
            for k in keys:
                sp = k.split('#')

                if len(sp) != 1:
                    sp[1] = int(sp[1])

                tmp_keys += sp

            keys = tmp_keys
            config_data = app_config
            for k in keys:
                config_data = config_data[k]

            return config_data
        else:
            return app_config[key]
    except:
        raise KeyError("Key "+str(key)+" not present in config file")
