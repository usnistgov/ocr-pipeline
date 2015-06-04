"""Prints a given configuration key from a given configuration file
"""
if __name__ == "__main__":
    import sys
    import os
    from apputils.config import *

    load_config(sys.argv[1], os.environ['ROOT'])
    print get_config(sys.argv[2])