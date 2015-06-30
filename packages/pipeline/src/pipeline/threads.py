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
        """Test if a thread is stopped

        Returns
            bool: True if stopped, False otherwise
        """
        return self.stop_event.isSet()

    def stop(self):
        """Stop the thread
        """
        self.stop_event.set()
