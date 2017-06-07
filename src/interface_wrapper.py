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
LINE_DATA_0 = 10
LINE_DATA_1 = 9
LINE_DATA_2 = 11

# 8-Bit ad-hoc digits
DPOS_DIGIT = [0, 1, 2, 3]
DPOS_NDIGITS = len(DPOS_DIGIT)
DPOS_GREEN_LED = 4
DPOS_RED_LED = 5
DPOS_BUZZER = 6
DPOS_UNUSED = 7  # Unused digit position = 7

DPOS_CONVERT = {  # 8-bit ad-hoc conversion
    0: [False, False, False],
    1: [True, False, False],
    2: [False, True, False],
    3: [True, True, False],
    4: [False, False, True],
    5: [True, False, True],
    6: [False, True, True],
    7: [True, True, True]
}

# Digit conversion matrix
# Works with [row][column]
DIGIT_CONVERT = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["*", "0", "#"],
]


class GpioLines:
    """
    A class that contains all of the gpio lines that are used.
    This allows for a nicer abstraction of the lines and some helper methods.
    """

    def __init__(self):
        self._lines = {
            "reg": GpioWrapper(LINE_REG_CLK),
            "io": GpioWrapper(LINE_IO_SWTICH),
            "d0": GpioWrapper(LINE_DATA_0),
            "d1": GpioWrapper(LINE_DATA_1),
            "d2": GpioWrapper(LINE_DATA_2)
        }
        self._digit_lines = ["d0", "d1", "d2"]

    @property
    def reg(self):
        return self._lines["reg"]

    @property
    def io(self):
        return self._lines["io"]

    def d(self, index):
        return self._lines[self._digit_lines[index]]

    def d_output(self):
        for d in self._digit_lines:
            self._lines[d].output()

    def d_input(self):
        for d in self._digit_lines:
            self._lines[d].input()

    def d_states(self):
        return [self._lines[d].state() for d in self._digit_lines]

    def d_all_high(self):
        high = True
        for s in self.d_states():
            high = high and s
        return high

    def d_all_low(self):
        return not self.d_all_high()

    def d_set_states(self, states):
        digits = [(self._lines[self._digit_lines[i]], states[i])
                  for i in range(len(self._digit_lines))]
        GpioWrapper.set_multiple_output(*digits)


class InterfaceWrapper:
    """
    The main class used by the startup to handle the interfacing.
    """

    def __init__(self, logger, DEMO_MODE=False):
        self.DEMO_MODE = DEMO_MODE
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        self.logger = logger
        self.gpio = GpioLines()
        self.gpio.reg.output()
        self.gpio.io.output()
        self.digit_received = Event()
        """The digit received event, fired when the class detects that a digit has been pressed"""
        self._run_loop = True
        self._current_digit = 0
        self._digit_down = False
        self._done_line_write = False
        # the follow store the value to apply to the given output on the next
        # pass
        self._led_green_apply = 0
        self._led_red_apply = 0
        self._buzzer_apply = 0

        self.logger.log("interface wrapper init complete")

    def main_loop(self):
        """
        Starts up the main loop of the interface, loop is wrapped in an exception handler that can handle both ‘Exception’ and ‘KeyboardInterrupt’.
        """
        self.logger.log("Main loop started")
        try:
            while self._run_loop:
                # write phase
                if self.DEMO_MODE:
                    input("> do write phase <")
                self._start_write()
                self._do_write_phase()
                # read phase
                if self.DEMO_MODE:
                    input("> do read phase <")
                self._start_read()
                self._do_read_phase()
        except Exception as ex:
            self.logger.loge(ex)
        except KeyboardInterrupt:
            self.logger.log("Beginning shutdown")

    def _inc_current_digit(self):
        self._current_digit += 1
        self._current_digit %= DPOS_NDIGITS

    def _dec_current_digit(self):
        self._current_digit -= 1
        self._current_digit %= DPOS_NDIGITS

    def _start_read(self):
        self.gpio.d_input()
        self.logger.logt("data lines set to input")
        GpioWrapper.wait()
        self.gpio.io.low()
        self.logger.logt("io line high")
        self.logger.logt("gpio lines configured to read")

    def _do_read_phase(self):
        if not self._done_line_write:
            self.logger.logt(
                "skipped reading rows due to previous write not being to column")
            return
        if self._digit_down:
            if self.gpio.d_all_high():
                self._digit_down = False
                self._inc_current_digit()
                self.logger.logt(
                    "digit no longer pressed, waiting for next input")
            else:
                self.logger.logt("digit still pressed")
        else:
            states = self.gpio.d_states()
            self.logger.logt("state readings: {}", states)
            active = None
            for s in range(len(states)):
                if not states[s]:
                    active = s
                    break
            if active is not None:
                self._digit_down = True
                self._dec_current_digit()
                dgt = DIGIT_CONVERT[self._current_digit][s]
                self.logger.logt("converted digit: {}", dgt)
                self.digit_received.fire(dgt)

    def _start_write(self):
        self.gpio.io.high()
        self.logger.logt("io line low")
        self.gpio.d_output()
        self.logger.logt("data lines set to output")
        self.logger.logt("gpio lines configured to write")

    def _do_write_phase(self):
        low_line = None
        self._done_line_write = False
        if self._led_green_apply:
            low_line = DPOS_GREEN_LED
            self._led_green_apply -= 1
            self.logger.logt("low line set to green LED")
        elif self._led_red_apply:
            low_line = DPOS_RED_LED
            self._led_red_apply -= 1
            self.logger.logt("low line set to red LED")
        elif self._buzzer_apply:
            low_line = DPOS_BUZZER
            self._buzzer_apply -= 1
            self.logger.logt("low line set to buzzer")
        else:  # apply keypad input
            low_line = DPOS_DIGIT[self._current_digit]
            if not self._digit_down:
                self._inc_current_digit()
            self._done_line_write = True
            self.logger.logt("low line set to next keypad row")
        # bin_out = bin(low_line)[2:].zfill(3)
        # self.logger.logt("gpio states: {}", bin_out)
        # self.gpio.d_set_states([bool(int(d)) for d in reversed(bin_out)])
        self.gpio.d_set_states(DPOS_CONVERT[low_line])
        self.gpio.reg.high()
        self.gpio.reg.low()
        #self.gpio.d_set_states([True, True, True])
        self.logger.logt("pulsed register line")

    def cleanup(self):
        """
        Cleans up any variables before exit.
        """
        self._run_loop = False
        gpio.cleanup()

    def flash_green_led(self):
        """
        Causes the green LED to flash once (if mid-flash, it will either do nothing or just reset the duration left on the flash, depending on how the hardware works).
        """
        self._led_green_apply = 2
        self.logger.log("green LED set to flash on next pass")

    def flash_red_led(self):
        """
        Causes the red LED to flash once (if mid-flash, it will either do nothing or just reset the duration left on the flash, depending on how the hardware works).
        """
        self._led_red_apply = 2
        self.logger.log("red LED set to flash on next pass")

    def beep_buzzer(self):
        """
        Causes the buzzer to go off once (if it is already buzzing, it will either do nothing or just reset the duration left on the buzz, depending on how the hardware works).
        """
        self._buzzer_apply = 2
        self.logger.log("buzzer set to activate on next pass")
