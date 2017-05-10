#! /usr/bin/env python3
import event
import logger
import io

TMP_LOG_FILE = "test.log"


class InferfaceWrapper_Test:
    def __init__(self):
        self.digit_received = event.Event()
        self.led_green_flashed = False
        self.led_red_flashed = False
        self.buzzer_enabled = False

    def flash_green_led(self):
        self.led_green_flashed = True

    def flash_red_led(self):
        self.led_red_flashed = True

    def beep_buzzer(self):
        self.buzzer_enabled = True


class Stdout_Test:
    def __init__(self):
        self._overwrite_line = ""

    @property
    def overwrite_line(self):
        return self._overwrite_line

    @overwrite_line.setter
    def overwrite_line(self, value):
        self._overwrite_line = value

    def start_overwrite_output(self):
        pass

    def end_overwrite_output(self):
        pass


class Logger_Test(logger.Logger):
    def __init__(self):
        super().__init__(TMP_LOG_FILE)
        self._out_file.close()
        self._out_file = io.StringIO()
