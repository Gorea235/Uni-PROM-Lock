import threading
import event

class Timeout(object):
    def __init__(self, length):
        self.__timer = threading.Timer(length, self.__timed_out)
        self.elapsed = event.Event()

    def start(self):
        self.__timer.start()

    def __timed_out(self):
        self.elapsed.fire()

    def reset(self):
        self.__timer.cancel()

    def cleanup(self):
        self.reset()
