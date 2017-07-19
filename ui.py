"""Manage the OCR pipeline, both remotely and locally

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
from __future__ import division
import logging
from os import listdir
import os
from apputils.config import load_config
from apputils.fileop import create_directories
from denoiser import Denoiser
from os.path import join, isdir, exists, abspath
from fabric.contrib.console import confirm
from fabric.contrib.project import upload_project
from fabric.contrib.files import exists as fab_exists
from fabric.decorators import task, roles, runs_once
from fabric.api import env, run, local, cd
from fabric.operations import sudo
from fabric.tasks import Task, execute
from fabric.state import output
from shutil import copytree, rmtree

# Initialize the app_config variable
load_config("conf/app.yaml", os.environ['ROOT'])
from apputils.config import app_config

logger = logging.getLogger('app')

# Hosts configurations
env.roledefs = app_config["machines"]
env.hosts = [ip for ips in env.roledefs.values() for ip in ips]

# Extra default configuration
env.warn_only = True
output.update({
    "warnings": False,
    "running": False
})

# Global variable to know if the execution is done locally or remotely
local_exec = False


# @task
# def install():
#     """Install the pipeline on the specified cluster
#     """
#     logger.debug("Installing pipeline...")
#
#     local_root = os.environ['ROOT']
#     remote_root = app_config['root']
#
#     if local_exec:
#         if abspath(local_root) == abspath(remote_root):
#             logger.error("Source and destination folder are the same")
#             exit(1)
#
#         if exists(remote_root):
#             if confirm("Existing data will be deleted. Do you want to proceed anyway?", default=False):
#                 rmtree(remote_root)
#             else:
#                 logger.error("Pipeline destination folder already exists")
#                 exit(2)
#
#         copytree(local_root, remote_root)
#         local(remote_root+'/utils/install.sh')
#     else:
#         if app_config["use_sudo"]:
#             run_fn = sudo
#         else:
#             run_fn = run
#
#         if not fab_exists(remote_root):
#             logging.debug("Building remote directory...")
#             run_fn("mkdir -p "+remote_root)
#         else:
#             if not confirm("Existing data will be deleted. Do you want to proceed anyway?", default=False):
#                 logger.error("Pipeline destination folder already exists")
#                 exit(2)
#
#         logging.debug("Uploading project...")
#         upload_project(
#             local_dir=local_root,
#             remote_dir=remote_root,
#             use_sudo=app_config["use_sudo"]
#         )
#
#         if run_fn(remote_root+"/utils/auth.sh").failed:
#             logger.error("An error occured with modifying the right for the pipeline")
#             exit(3)
#
#         if run(remote_root+"/utils/install.sh").failed:
#             logger.error("An error occured with the install script")
#             exit(4)
#
#     logger.info("Pipeline successfully installed")


@task
def init():
    """Initialize the app (available for localhost only)
    """
    logger.debug("Initializing app...")

    if not local_exec:
        logger.error("Pipeline can only be initialized locally")
        exit(1)

    # Create project tree
    create_directories(app_config["dirs"])
    logger.info("App initialized")


@task
def create_models(dataset_dir):
    """Initialize the app (available for localhost only)

    Parameters:
        dataset_dir (:func:`str`): Path to the training set
    """
    logger.debug("Creating models...")

    if not local_exec:
        logger.error("Models can only be generated locally")
        exit(1)

    # Modify the configuration for local execution
    app_config['root'] = os.environ['ROOT']

    # Generate inline models and train classifier
    denoiser = Denoiser(app_config)

    if not exists(dataset_dir) or not isdir(dataset_dir):
        logger.error(dataset_dir+" is not a valid directory")
        exit(2)

    dataset = [join(dataset_dir, f) for f in listdir(dataset_dir)]

    denoiser.generate_models(dataset)
    logger.info("Inline models generated")

    denoiser.train(dataset)
    logger.info("Classifier trained")


@task
def check():
    """Check that the 3rd party software are all installed
    """
    base_dir = "utils/check"
    scripts = [join(base_dir, sc) for sc in listdir(base_dir) if sc.endswith(".sh")]

    for script in scripts:
        launch_script(script)


# @task
# @runs_once
# def start_pipeline():
#     """Start the conversion process across the platform.
#     """
#     execute(start_master)
#     execute(start_slave)


@task
@roles("master")
def start_master():
    """Start the master server on the local machine
    """
    launch_script("utils/run-wrapper.sh", ["--master", ("> %s/master.log", app_config["dirs"]["logs"])], True)


@task
@roles("slaves")
def start_slave():
    """Start a slave on the local machine
    """
    launch_script("utils/run-wrapper.sh", ["--slave", ("> %s/slave.log", app_config["dirs"]["logs"])], True)


def launch_script(script_name, script_opts=list(), background=False):
    """Launch any script you specify

    Parameters:
        script_name (:func:`str`): Path of the script to run
        script_opts (:func:`str`): Options to pass to the script
    """
    if local_exec:
        root_dir = os.environ['ROOT']
    else:
        root_dir = app_config['root']

    command = join(root_dir, script_name)+" "+" ".join(script_opts)

    logger.debug("Execute: "+command)

    with cd(root_dir):
        if local_exec:
            if background:
                local(command)
                return

            if local(command).failed:
                logger.error("Command failed "+command)
                exit(1)
        else:
            if background:
                run(command)
                return

            if run(command).failed:
                logger.error("Command failed "+command)
                exit(1)


def print_help(light=False):
    """Print the help message

    Parameter
        light (bool): If true, only print the usage
    """
    print "Usage: python ui.py [-h] command [args [args ...]]"

    if light:
        return

    print "Commands: "

    default_func_help = "No description available"
    for func in functions.keys():
        help_str = "* "+func+" "*(20-len(func))

        if func in functions_help.keys():
            help_str += functions_help[func]
        else:
            help_str += default_func_help

        print help_str

    print ""
    print "Options:"
    print_opts = ', '.join(help_opts)

    print print_opts+" "*(22-len(print_opts))+"Print this help message"


def setup_local_exec():
    """Set the local_exec variable to true
    """
    global local_exec
    local_exec = True


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    setup_local_exec()

    help_opts = ["--help", "-h"]
    functions = {k: v for k, v in locals().items() if isinstance(v, Task) and v.__module__ == "__main__"
                 and k != "print_help"}
    functions_help = {k: v.__doc__.split("\n")[0] for k, v in functions.items() if v.__doc__ is not None}

    if len(args) == 0:
        logger.error("No function specified")
        print_help(True)
        exit(1)

    if len(args) == 1 and args[0] in help_opts:
        print_help()
        exit(0)

    if args[0] not in functions.keys():
        logger.fatal("Command "+args[0]+" unknown")
        print_help(True)
        exit(1)

    if len(args) > 1:
        functions[args[0]](*args[1:])
    else:
        functions[args[0]]()


