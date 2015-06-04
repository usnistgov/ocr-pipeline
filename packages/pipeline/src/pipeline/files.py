"""Package defining Redis file manager
"""
import base64
from os import remove
import redis


class FileManager(object):
    """Redis file manager
    """

    def __init__(self, host="127.0.0.1", port=6379, db=0):
        self.server = redis.StrictRedis(host, port, db)
        self.hashmap_name = "fman"

    def retrieve_file(self, filename):
        b64_hash = self.server.hget(self.hashmap_name, filename)
        data = base64.b64decode(b64_hash)

        with open(filename, 'wb') as zip_file:
            zip_file.write(data)

    def store_file(self, filename):
        with open(filename, 'rb') as zip_file:
            b64_hash = base64.b64encode(zip_file.read())

        self.server.hset(self.hashmap_name, filename, b64_hash)
        remove(filename)

    def delete_file(self, filename):
        self.server.hdel(self.hashmap_name, filename)
