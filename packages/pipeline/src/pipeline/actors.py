"""Package defining master and slave threads

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
import logging
from os import listdir, getpid, remove
from os.path import join, exists, split
from socket import gethostbyname, gethostname
from time import sleep
from shutil import move
from pipeline.files import FileManager
from pipeline.threads import StoppableThread
from pipeline.utils import create_data_directory
from pipeline.logger import AppLogger, LogWriter
from pipeline.queue import QueueManager, CommandQueueItem


class Master(StoppableThread):
    """ Master worker
    """

    def __init__(self, app_config):
        StoppableThread.__init__(self)

        # ip = app_config["machines"]["master"][0].split('@')
        # master_ip = ip[-1:][0]
        redis_ip = app_config["redis"]["host"]
        redis_port = app_config["redis"]["port"]

        self.logger = AppLogger("master", logging.getLogger("local"), redis_ip, redis_port)
        self.log_writer = LogWriter(logging.getLogger("app"), redis_ip, redis_port)

        self.command_queue = QueueManager(host=redis_ip, port=redis_port, qname="commands")
        self.finished_queue = QueueManager(host=redis_ip, port=redis_port, qname="finished")
        # self.fman = FileManager(master_ip, master_queue_port)
        self.fman = FileManager(app_config)

        self.config = app_config
        self.input = app_config["dirs"]["input"]
        self.output = app_config["dirs"]["output"]

    def run(self):
        self.log_writer.start()
        self.logger.info("Starting master...")

        # processed_filenames = []

        while not self.is_stopped():
            self.logger.info("Reading input directory...")
            # filenames = [f for f in listdir(self.input) if f not in processed_filenames]
            filenames = listdir(self.input)

            if len(filenames) > 0:
                self.logger.info(str(len(filenames)) + " file(s) to put in the queue")

                for filename in filenames:
                    self.logger.debug("Processing %s..." % filename)
                    full_filename = join(self.input, filename)
                    dirname = create_data_directory(full_filename, self.config["dirs"]["temp"])
                    self.logger.debug("%s has been created." % dirname)

                    if dirname is not None:
                        # archive = zip_directory(dirname)

                        # self.fman.store_file(archive)
                        self.command_queue.push(CommandQueueItem(filename=dirname, logger=self.logger,
                                                                 config=self.config))

                    # processed_filenames.append(filename)
                    self.logger.info("Incoming files have been put in the queue")

            if len(self.finished_queue) > 0:
                self.logger.info("Finished queue not empty")

                while not self.finished_queue.is_empty():
                    filename = self.finished_queue.pop()
                    # self.fman.retrieve_file(filename)

                    output_file_path = join(self.config["dirs"]["output"], split(filename)[1])
                    if exists(output_file_path):
                        remove(output_file_path)

                    move(filename, self.config["dirs"]["output"])
                    # self.fman.delete_file(filename)

                self.logger.info("No more finished job to process")

            sleep(60)  # Avoid CPU consuption while waiting

    def stop(self):
        self.logger.info("Master stopped")

        self.log_writer.stop()
        StoppableThread.stop(self)


class Slave(StoppableThread):
    """ Slave worker
    """

    def __init__(self, app_config):
        StoppableThread.__init__(self)

        self.config = app_config

        # ip = app_config["machines"]["master"][0].split('@')
        # master_ip = ip[-1:][0]
        redis_ip = app_config["redis"]["host"]
        redis_port = app_config["redis"]["port"]

        self.command_queue = QueueManager(host=redis_ip, port=redis_port, qname="commands")
        self.finished_queue = QueueManager(host=redis_ip, port=redis_port, qname="finished")
        # self.fman = FileManager(master_ip, master_queue_port)

        slave_ip = gethostbyname(gethostname())
        slave_pid = getpid()
        uid = slave_ip + "::" + str(slave_pid)

        self.logger = AppLogger(uid, logging.getLogger("local"), redis_ip, redis_port)
        self.max_tries = app_config["commands"]["tries"]

        self.logger.info("Slave initiated [redis on "+redis_ip+"]")

    def run(self):
        self.logger.info("Starting slave...")

        while not self.is_stopped():
            if not self.command_queue.is_empty():
                cmd_json = self.command_queue.pop()
                cmd = CommandQueueItem(jsondata=cmd_json, logger=self.logger, config=self.config)

                status = cmd.execute()

                # Job returned an error and has reached the limit of tries
                if status == 1 and cmd.tries >= self.max_tries:
                    self.logger.error("Error when processing command")
                    continue

                if cmd.current_step == -1:
                    self.logger.info("Pushing to finished queue")
                    self.finished_queue.push(cmd.filename)
                    self.logger.info("Job done")
                    continue

                self.command_queue.push(cmd)

            sleep(1)  # Avoid CPU consumption while waiting

    def stop(self):
        self.logger.info("Slave stopped")
        StoppableThread.stop(self)
