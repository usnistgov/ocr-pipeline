"""This script launches the pipeline on the local machine. The user specify the actor to start on the command line.

For more information on how this script works, you can use the following command::

    $ python2 run.py --help

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
import os

if __name__ == "__main__":
    from pipeline import run_master, run_slave
    import argparse

    from apputils.config import load_config
    load_config("conf/app.yaml", os.environ['ROOT'])

    from apputils.config import app_config

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--slave", action="store_true", help="launch a slave process")
    parser.add_argument("-m", "--master", action="store_true", help="launch a master process")
    args = parser.parse_args()

    if args.master == args.slave:
        print "Please choose what kind of process to launch"
        parser.print_help()
        exit()
    elif args.master:
        print "Starting master..."
        run_master(app_config)
    elif args.slave:
        print "Starting slave..."
        run_slave(app_config)
