"""Package defining master and slave threads
"""
import logging
from os import listdir, getpid, remove
from os.path import join, exists, split
from socket import gethostbyname, gethostname
from time import sleep
from shutil import move
from apputils.fileop import zip_directory
from pipeline.files import FileManager
from pipeline.threads import StoppableThread
from pipeline.utils import create_data_directory
from pipeline.logger import AppLogger, LogWriter
from pipeline.queue import QueueManager, CommandQueueItem


class Master(StoppableThread):
    """Master worker
    """

    def __init__(self, app_config):
        StoppableThread.__init__(self)

        ip = app_config["machines"]["master"][0].split('@')
        master_ip = ip[-1:][0]
        master_queue_port = app_config["redis"]["port"]

        self.logger = AppLogger("master", logging.getLogger("local"), master_ip, master_queue_port)
        self.log_writer = LogWriter(logging.getLogger("app"))

        self.command_queue = QueueManager(host=master_ip, port=master_queue_port, qname="commands")
        self.finished_queue = QueueManager(host=master_ip, port=master_queue_port, qname="finished")
        self.fman = FileManager(master_ip, master_queue_port)

        self.config = app_config
        self.input = app_config["dirs"]["input"]
        self.output = app_config["dirs"]["output"]

    def run(self):
        self.log_writer.start()
        self.logger.debug("Running master...")

        processed_filenames = []

        while not self.is_stopped():
            self.logger.debug("Reading directory...")
            filenames = [f for f in listdir(self.input) if f not in processed_filenames]

            if len(filenames) > 0:
                self.logger.info(str(len(filenames)) + " file(s) to put in the queue")

            for filename in filenames:
                full_filename = join(self.input, filename)
                dirname = create_data_directory(full_filename)

                if dirname is not None:
                    archive = zip_directory(dirname)

                    self.fman.store_file(archive)
                    self.command_queue.push(CommandQueueItem(filename=archive, logger=self.logger, config=self.config))

                processed_filenames.append(filename)

            if len(self.finished_queue) > 0:
                self.logger.info("Finished queue not empty")

                while not self.finished_queue.is_empty():
                    filename = self.finished_queue.pop()
                    self.fman.retrieve_file(filename)

                    output_file_path = join(self.config["dirs"]["output"], split(filename)[1])
                    if exists(output_file_path):
                        remove(output_file_path)

                    move(filename, self.config["dirs"]["output"])
                    self.fman.delete_file(filename)

                self.logger.info("No more finished job to process")

            sleep(60)  # Avoid CPU consuption while waiting

    def stop(self):
        self.logger.info("Master stopped")

        self.log_writer.stop()
        StoppableThread.stop(self)


class Slave(StoppableThread):
    """Slave worker
    """

    def __init__(self, app_config):
        StoppableThread.__init__(self)

        self.config = app_config

        ip = app_config["machines"]["master"][0].split('@')
        master_ip = ip[-1:][0]
        master_queue_port = app_config["redis"]["port"]

        self.command_queue = QueueManager(host=master_ip, port=master_queue_port, qname="commands")
        self.finished_queue = QueueManager(host=master_ip, port=master_queue_port, qname="finished")
        self.fman = FileManager(master_ip, master_queue_port)

        slave_ip = gethostbyname(gethostname())
        slave_pid = getpid()
        uid = slave_ip + "::" + str(slave_pid)

        self.logger = AppLogger(uid, logging.getLogger("local"), master_ip, master_queue_port)
        self.max_tries = app_config["commands"]["tries"]

        self.logger.info("Slave initiated [redis on "+master_ip+"]")

    def run(self):
        self.logger.debug("Running slave...")

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