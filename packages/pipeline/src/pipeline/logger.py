"""Package handling different loggers

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
import json
import logging
from time import sleep
from pipeline.threads import StoppableThread
from pipeline.queue import QueueManager


class AppLogger(object):
    """Logger publishing to a redis queue
    """

    def __init__(self, uid, local_logger, queue_ip="127.0.0.1", queue_port=6379):
        self.log_queue = QueueManager(host=queue_ip, port=queue_port, qname="logging")
        self.logger = local_logger

        # Identify the logging process
        self.uid = uid

    def log(self, level, message):
        """Log a message with a given level

        Parameters
            level (int): Log level
            message (str): Message to store
        """
        log_mess = {
            "uid": self.uid,
            "lvl": level,
            "msg": message
        }

        self.log_queue.push(json.dumps(log_mess))
        self.logger.log(level, "["+self.uid+"] "+message)

    def debug(self, message):
        """Log a debug message

        Parameters
            message (str): Message to store
        """
        self.log(logging.DEBUG, message)

    def info(self, message):
        """Log an info message

        Parameters
            message (str): Message to store
        """
        self.log(logging.INFO, message)

    def warning(self, message):
        """Log a warning message

        Parameters
            message (str): Message to store
        """
        self.log(logging.WARNING, message)

    def error(self, message):
        """Log an error message

        Parameters
            message (str): Message to store
        """
        self.log(logging.ERROR, message)

    def fatal(self, message):
        """Log a fatal message

        Parameters
            message (str): Message to store
        """
        self.log(logging.FATAL, message)


class LogWriter(StoppableThread):
    """Pops element from the logging queue and write them in the proper directory
    """

    def __init__(self, app_logger):
        StoppableThread.__init__(self)

        self.log_queue = QueueManager(qname="logging")
        self.logger = app_logger

    def write_logs(self):
        """Write logs to a local file
        """
        while not self.log_queue.is_empty():
            log_json = self.log_queue.pop()
            log_data = json.loads(log_json)

            self.logger.log(log_data["lvl"], "["+log_data["uid"]+"] "+log_data["msg"])
            sleep(0.2)

    def run(self):
        self.logger.debug("Logger initiatied")

        while not self.stop_event.isSet():
            self.write_logs()
            sleep(0.5)

        self.write_logs()
        self.logger.info("Logger stopped")
