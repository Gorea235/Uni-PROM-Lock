#! /usr/bin/env python3
from code_lock import CodeLock
from event import Event
from interface_wrapper import InterfaceWrapper
from logger import *
from stdout import StdoutOverwrite

LOG_FILE = "events.log"


class App:
    def __init__(self):
        """
        Main entry point of application
        """
        self._cleanup_event = Event()
        self.stdout = StdoutOverwrite()
        self.logger = Logger(LOG_FILE)
        self.logger.trace_level = TRACE
        self.iface = InterfaceWrapper(self.logger)
        self.internal = CodeLock(self.iface, self.logger, self.stdout)
        self.wrap(self.stdout, self.logger, self.iface, self.internal)

        self.iface.main_loop()  # this cannot except unless logger causes an issue

        self._cleanup_event.fire()

    def wrap(self, *args):
        for c in args:
            self._cleanup_event.bind(c.cleanup)


if __name__ == "__main__":
    App()
