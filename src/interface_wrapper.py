#! /usr/bin/env python3
import RPi.GPIO as gpio
from event import Event
from gpio_wrapper import GpioWrapper

# GPIO States
GPIO_S_HIGH = "1"
GPIO_S_LOW = "0"

# GPIO lines
LINE_REG_CLK = 14
LINE_IO_SWTICH = 15
LINE_DATA_0 = 11
LINE_DATA_1 = 9
LINE_DATA_2 = 10

# 8-Bit ad-hoc digits
DPOS_DIGIT = [0, 1, 2, 3]
DPOS_NDIGITS = len(DPOS_DIGIT)
DPOS_GREEN_LED = 4
DPOS_RED_LED = 5
DPOS_BUZZER = 6
# == # Unused digit position = 7
 
DPOS_MAX = 7

# Digit conversion matrix
# Works with [row][column]
DIGIT_CONVERT = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["*", "0", "#"],
]

# Whether the looped code should log
LOG_LOOP = False


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

    def d(self, index):
        return self.__lines[self.__digit_lines[index]]

    def d_output(self):
        for d in self.__digit_lines:
            self.__lines[d].output()

    def d_input(self):
        for d in self.__digit_lines:
            self.__lines[d].input()

    def d_states(self):
        return [self.__lines[d].state() for d in self.__digit_lines]

    def d_all_high(self):
        high = True
        for s in self.d_states():
            high = high and s
        return high

    def d_all_low(self):
        return not self.d_all_high()

    def d_set_states(self, states):
        digits = [(self.__lines[self.__digit_lines[i]], states[i])
                  for i in range(len(self.__digit_lines))]
        GpioWrapper.set_multiple_output(*digits)


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
        self.__current_digit = 0
        self.__digit_down = False
        # the follow store the value to apply to the given output on the next
        # pass
        self.__led_green_apply = False
        self.__led_red_apply = False
        self.__buzzer_apply = False

    def llog(self, line, *args):
        """
        Will only log at level debug if constant is True.
        """
        if LOG_LOOP:
            self.logger.logd(line, args)

    def main_loop(self):
        """
        Starts up the main loop of the interface, loop is wrapped in an exception handler that can handle both ‘Exception’ and ‘KeyboardInterrupt’.
        """
        try:
            while self.__run_loop:
                # write phase
                self.__do_write_phase()
                # read phase
                self.__do_read_phase()
        except Exception as ex:
            self.logger.loge(ex)
        except KeyboardInterrupt:
            self.logger.log("Code lock shutting down")

    def __start_read(self):
        self.gpio.reg.low()
        self.llog("register line low")
        self.gpio.d_input()
        self.llog("data lines set to input")
        self.gpio.io.high()
        self.llog("io line high")
        self.llog("gpio lines configured to read")

    def __do_read_phase(self):
        self.__start_read()
        if self.__digit_down:
            if self.gpio.d_all_high():
                self.__digit_down = False
                self.llog("digit no longer pressed, waiting for next input")
            else:
                states = self.gpio.d_states()
                self.llog("state readings: {}", states)
                active = None
                for s in range(len(states)):
                    if states[s]:
                        active = s
                        break
                if active is not None:
                    self.__digit_down = True
                    dgt = DIGIT_CONVERT[self.__current_digit][s]
                    self.llog("converted digit: {}", dgt)
                    self.digit_received.fire(dgt)

    def __start_write(self):
        self.gpio.io.low()
        self.llog("io line low")
        self.gpio.d_output()
        self.llog("data lines set to output")
        self.gpio.reg.high()
        self.llog("register line high")
        self.llog("gpio lines configured to write")

    def __do_write_phase(self):
        self.__start_write()
        low_line = None
        if self.__led_green_apply:
            low_line = DPOS_GREEN_LED
            self.__led_green_apply = False
            self.llog("low line set to green LED")
        elif self.__led_red_apply:
            low_line = DPOS_RED_LED
            self.__led_red_apply = False
            self.llog("low line set to red LED")
        elif self.__buzzer_apply:
            low_line = DPOS_BUZZER
            self.__buzzer_apply = False
            self.llog("low line set to buzzer")
        else:  # apply keypad input
            low_line = DPOS_DIGIT[self.__current_digit]
            self.__current_digit += 1
            self.__current_digit %= DPOS_NDIGITS
            self.llog("low line set to next keypad row")
        bin_out = bin(low_line)[2:]
        self.llog("gpio states: {}", bin_out)
        self.gpio.d_set_states([bool(int(d)) for d in bin_out])

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
