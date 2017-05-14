#! /usr/bin/env python3
#from code_lock import CodeLock
import code_lock
from event import *
from interface_wrapper import InterfaceWrapper
from logger import *
from stdout import StdoutOverwrite

import traceback

LOG_FILE = "events.log"
DEMO_MODE = False
DEMO_DIGIT_INPUT_DIGITS_IMM = [("1", 2), ("2", 2), ("5", 2),
                               ("4", 2),
                               ("8", 2),
                               ("1", 4),
                               ("1", 2), ("2", 2), ("3", 2), ("4", 4),
                               ("6", 2),
                               ("2", 1),
                               ("2", 1),
                               ("2", 1),
                               ("2", 1),
                               ("2", 1),
                               ("3", 1)]
DEMO_DIGIT_INPUT_DIGITS_NIMM = [("1", 2), ("4", 2), ("2", 2), ("6", 4),
                                ("3", 2), ("7", 4),
                                ("1", 2), ("2", 2), ("3", 2), ("4", 4),
                                ("2", 1), ("2", 1), ("2", 1), ("2", 4),
                                ("2", 1), ("2", 1), ("2", 1), ("2", 4),
                                ("2", 1), ("2", 1), ("2", 1), ("2", 4),
                                ("2", 1), ("2", 1), ("2", 1), ("2", 4),
                                ("2", 1), ("2", 1), ("2", 1), ("2", 4),
                                ("3", 1)]


class App:
    def __init__(self):
        """
        Main entry point of application
        """
        self._cleanup_event = Event()
        self.stdout = StdoutOverwrite()
        self.logger = Logger(LOG_FILE)
        self.logger.trace_level = INFO
        self.iface = InterfaceWrapper(self.logger, DEMO_MODE)
        self.internal = code_lock.CodeLock(
            self.iface, self.logger, self.stdout, DEMO_MODE)
        self.wrap(self.stdout, self.logger, self.iface, self.internal)

        if not DEMO_MODE:
            self.iface.main_loop()  # this cannot except unless logger causes an issue
        else:
            import time

            try:
                input("> start main loop demo <")
                self.iface.main_loop()
            except KeyboardInterrupt:
                print("main loop exited")

            input("> start digit demo <")

            def test_digits(dgts):
                for c in dgts:
                    self.internal.digit_received_handler(c[0])
                    time.sleep(c[1])
            code_lock.IMMEDIATE_REJECT = True
            test_digits(DEMO_DIGIT_INPUT_DIGITS_IMM)
            code_lock.IMMEDIATE_REJECT = False
            test_digits(DEMO_DIGIT_INPUT_DIGITS_NIMM)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

        try:
            self._cleanup_event.fire()
        except EventException as ex:
            traceback.format_exc()
            print(ex)
            for e in ex._exc:
                print(e)

    def wrap(self, *args):
        for c in args:
            self._cleanup_event.bind(c.cleanup)


if __name__ == "__main__":
    App()
