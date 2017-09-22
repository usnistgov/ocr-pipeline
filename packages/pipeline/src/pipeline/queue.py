""" Package defining Redis queue

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
import redis
from pipeline.commands import *


class QueueManager(object):
    """ Redis queue manager.
    """

    def __init__(self, host="127.0.0.1", port=6379, db=0, qname=None):
        self.server = redis.StrictRedis(host, port, db)

        if qname is not None:
            self.queue_name = qname
        else:
            self.queue_name = "default"

    def push(self, json_object):
        """Push JSON on a redis queue

        Parameters
            json_object (dict): JSON to push to redis
        """
        self.server.rpush(self.queue_name, json_object)

    def pop(self):
        """Pop object from a redis queue

        Returns
            dict: JSON from redis
        """
        return self.server.lpop(self.queue_name)

    def is_empty(self):
        """Test if the queue is empty or not

        Returns
            bool: True if empty, false otherwise
        """
        return len(self) == 0

    def __len__(self):
        return self.server.llen(self.queue_name)


class CommandQueueItem(object):
    """ Command stored in the redis queue.
    """

    def __init__(self, filename="", jsondata="", logger=None, config=None):
        if filename != "":
            self.current_step = 0
            self.filename = filename
            self.tries = 0
        else:  # Rebuild command from JSON
            data = json.loads(jsondata)
            self.current_step = data["command"]
            self.filename = data["filename"]
            self.tries = data["tries"]

        # self.filename = join(self.filename)
        self.logger = logger
        self.config = config

        # Building the command list
        self.steps = []
        for cmd in self.config["commands"]["list"]:
            cmd_class = None
            cmd_config = self.config

            if type(cmd) == str:
                cmd_class = eval(cmd)
            elif type(cmd) == dict:
                if len(cmd.keys()) == 1:
                    cmd_class = eval(cmd.keys()[0])
                    cmd_config["command"] = cmd.values()[0]
            if cmd_class is None:
                self.logger.fatal("Unreadable command list")
                raise SyntaxError(
                    "Command list is not correctly formatted"
                )

            self.steps.append(
                cmd_class(self.filename, self.logger, cmd_config)
            )

    def execute(self):
        """Execute the command

        Returns:
            int: 0 when no errors happen, >0 otherwise
        """
        command = self.steps[self.current_step]
        cmd_result = command.execute()

        if cmd_result == 1:  # The process has failed
            self.tries += 1
            return 1

        # Current step is incremented
        self.current_step += 1

        # Stop flag
        if self.current_step >= len(self.steps):
            self.current_step = -1
            self.tries = 0

        return 0

    def __str__(self):
        repr_str = {
            "command": self.current_step,
            "filename": self.filename,
            "tries": self.tries
        }

        return json.dumps(repr_str)



