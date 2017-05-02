#! /usr/bin/env python3
import time
import RPi.GPIO as gpio

HARDWARE_WAIT = 0.010
BOUNCE_SEARCH = 0.005


class GpioWrapper:
    def __init__(self, pin):
        self._pin = pin
        self._io_inp = True
    
    @staticmethod
    def set_multiple_output(*args):
        for t in args:
            t[0]._apply_output(t[1])
        time.sleep(HARDWARE_WAIT)

    def set_io(self, state):
        gpio.setup(self._pin, state)

    def input(self):
        self.set_io(gpio.IN)

    def output(self):
        self.set_io(gpio.OUT)

    def set_output(self, value):
        self._apply_output(value)
        time.sleep(HARDWARE_WAIT)
    
    def _apply_output(self, value):
        assert isinstance(value, bool)
        gpio.output(self._pin, value)

    def high(self):
        self.set_output(True)

    def low(self):
        self.set_output(False)

    def state(self):
        start = time.time()
        total_states = 0
        states_caught = 0
        while time.time() - start < BOUNCE_SEARCH:
            total_states = gpio.input(self._pin)
            states_caught += 1
        avg = total_states / states_caught
        return round(avg)
    
    @property
    def is_high(self):
        return self.state() == 1
    
    @property
    def is_low(self):
        return self.state() == 0
