"""Package defining Redis file manager

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
import base64
from os import remove
import redis


class FileManager(object):
    """Redis file manager
    """

    # def __init__(self, host="127.0.0.1", port=6379, db=0):
    #     self.server = redis.StrictRedis(host, port, db)
    #     self.hashmap_name = "fman"
    def __init__(self, app_config):
        self.hashmap = {}  # Stores fileid -> filepath
        self.config = app_config

    # def retrieve_file(self, filename):
    #     """Retrieve from redis hashmap
    #
    #     Args
    #         filename (str): Filename to retrieve
    #     """
    #     b64_hash = self.server.hget(self.hashmap_name, filename)
    #     data = base64.b64decode(b64_hash)
    #
    #     with open(filename, 'wb') as zip_file:
    #         zip_file.write(data)
    #
    # def store_file(self, filename):
    #     """Store file to redis hashmap
    #
    #     Args
    #         filename (str): Filename to store
    #     """
    #     with open(filename, 'rb') as zip_file:
    #         b64_hash = base64.b64encode(zip_file.read())
    #
    #     self.server.hset(self.hashmap_name, filename, b64_hash)
    #     remove(filename)

    def delete_file(self, filename):
        """Delete file from redis hashmap

        Args
            filename (str): Filename to delete
        """
        # self.server.hdel(self.hashmap_name, filename)
        if filename not in self.hashmap:
            raise KeyError("FileManager: filename is not present in hashmap")

        del self.hashmap[filename]
