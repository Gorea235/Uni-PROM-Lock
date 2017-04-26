import threading
import event

class Timeout(object):
    """
    The timeout class used to raise an event when the given time has elapsed.
    """

    def __init__(self, length):
        self.__timer = threading.Timer(length, self.__timed_out)
        self.elapsed = event.Event()
        """The elapsed event, fires when timeout completes."""

    def start(self):
        """
        Starts timeout from current time (without resetting the time length).
        """
        self.__timer.start()

    def __timed_out(self):
        self.elapsed.fire()

    def reset(self):
        """
        Stops timeout and reset the time remaining back to full timeout length.
        """
        self.__timer.cancel()

    def restart(self):
        """
        Resets and starts the timeout.
        """
        self.reset()
        self.start()

    def cleanup(self):
        """
        Cleans up class.
        """
        self.reset()
