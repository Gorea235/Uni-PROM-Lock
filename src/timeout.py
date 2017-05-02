#! /usr/bin/env python3
import threading
import event


class Timeout(object):
    """
    The timeout class used to raise an event when the given time has elapsed.
    """

    def __init__(self, length):
        self._timer = threading.Timer(length, self._timed_out)
        self.elapsed = event.Event()
        """The elapsed event, fires when timeout completes."""

    def start(self):
        """
        Starts timeout from current time (without resetting the time length).
        """
        self._timer.start()

    def _timed_out(self):
        self.elapsed.fire()

    def reset(self):
        """
        Stops timeout and reset the time remaining back to full timeout length.
        """
        self._timer.cancel()

    def restart(self):
        """
        Resets and starts the timeout.
        """
        self.reset()
        self.start()
    
    @property
    def active(self):
        return self._timer.is_alive()

    def cleanup(self):
        """
        Cleans up class.
        """
        self.reset()
