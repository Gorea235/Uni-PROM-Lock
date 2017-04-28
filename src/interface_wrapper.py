#! /usr/bin/env python3
import RPi.GPIO as gpio
from event import Event
from gpio_wrapper import GpioWrapper

LINE_REG_CLK = 14
LINE_IO_SWTICH = 15
LINE_DATA_0 = 11
LINE_DATA_1 = 9
LINE_DATA_2 = 10


class GpioLines:
    """
    A class that contains all of the gpio lines that are used.
    This allows for a nicer abstraction of the lines and some helper methods.
    """

    def __init__(self):
        self.__lines = {
            "reg": GpioWrapper(LINE_REG_CLK),
            "io": GpioWrapper(LINE_IO_SWTICH),
            "d0": GpioWrapper(LINE_DATA_0),
            "d1": GpioWrapper(LINE_DATA_1),
            "d2": GpioWrapper(LINE_DATA_2)
        }
        self.__digit_lines = ["d0", "d1", "d2"]

    @property
    def reg(self):
        return self.__lines["reg"]

    @property
    def io(self):
        return self.__lines["io"]

    @property
    def d0(self):
        return self.__lines["d0"]

    @property
    def d1(self):
        return self.__lines["d1"]

    @property
    def d2(self):
        return self.__lines["d2"]

    def d_output(self):
        for d in self.__digit_lines:
            self.__lines[d].output()

    def d_input(self):
        for d in self.__digit_lines:
            self.__lines[d].input()


class InterfaceWrapper:
    """
    The main class used by the startup to handle the interfacing.
    """

    def __init__(self, logger, main):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        self.logger = logger
        self.gpio = GpioLines()
        self.digit_received = Event()
        """The digit received event, fired when the class detects that a digit has been pressed"""
        self.__run_loop = True
        # the follow store the value to apply to the given output on the next
        # pass
        self.__led_green_apply = False
        self.__led_red_apply = False
        self.__buzzer_apply = False

    def main_loop(self):
        """
        Starts up the main loop of the interface, loop is wrapped in an exception handler that can handle both ‘Exception’ and ‘KeyboardInterrupt’.
        """
        try:
            while self.__run_loop:
                pass
        except Exception as ex:
            self.logger.loge(ex)
        except KeyboardInterrupt:
            self.logger.log("Code lock shutting down")

    def __start_read(self):
        self.gpio.reg.low()
        # self.logger.logd("register line low")
        self.gpio.d_input()
        # self.logger.logd("data lines set to input")
        self.gpio.io.high()
        # self.logger.logd("io line high")
        # self.logger.logd("gpio lines configured to read")

    def __start_write(self):
        self.gpio.io.low()
        # self.logger.logd("io line low")
        self.gpio.d_output()
        # self.logger.logd("data lines set to output")
        self.gpio.reg.high()
        # self.logger.logd("register line high")
        # self.logger.logd("gpio lines configured to write")

    def cleanup(self):
        """
        Cleans up any variables before exit.
        """
        self.logger.log("cleaning up interface usage")
        self.__run_loop = False
        gpio.cleanup()

    def flash_green_led(self):
        """
        Causes the green LED to flash once (if mid-flash, it will either do nothing or just reset the duration left on the flash, depending on how the hardware works).
        """
        self.__led_green_apply = True
        self.logger.log("green LED set to flash on next pass")

    def flash_red_led(self):
        """
        Causes the red LED to flash once (if mid-flash, it will either do nothing or just reset the duration left on the flash, depending on how the hardware works).
        """
        self.__led_red_apply = True
        self.logger.log("red LED set to flash on next pass")

    def beep_buzzer(self):
        """
        Causes the buzzer to go off once (if it is already buzzing, it will either do nothing or just reset the duration left on the buzz, depending on how the hardware works).
        """
        self.__buzzer_apply = True
        self.logger.log("buzzer set to activate on next pass")
