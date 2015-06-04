"""Utility package for threads
"""
from threading import Thread, Event


class StoppableThread(Thread):
    """A thread with the ability to be remotely stopped
    """

    def __init__(self):
        Thread.__init__(self)
        self.stop_event = Event()

    def is_stopped(self):
        return self.stop_event.isSet()

    def stop(self):
        self.stop_event.set()