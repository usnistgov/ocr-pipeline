"""Utility package for threads

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