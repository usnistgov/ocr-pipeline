"""Prints a given configuration key from a given configuration file

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
if __name__ == "__main__":
    import sys
    import os
    from apputils.config import *

    load_config(sys.argv[1], os.environ['ROOT'])
    print get_config(sys.argv[2])
