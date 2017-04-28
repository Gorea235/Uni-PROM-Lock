#! /usr/bin/env python3
import time
import RPi.GPIO as gpio

HARDWARE_WAIT = 0.010
BOUNCE_SEARCH = 0.005


class GpioWrapper:
    def __init__(self, pin):
        self.__pin = pin
        self.__io_inp = True

    def set_io(self, state):
        gpio.setup(self.__pin, state)

    def input(self):
        self.set_io(gpio.IN)

    def output(self):
        self.set_io(gpio.OUT)

    def set_output(self, value):
        assert isinstance(value, bool)
        gpio.output(self.__pin, value)
        time.sleep(HARDWARE_WAIT)

    def high(self):
        self.set_output(True)

    def low(self):
        self.set_output(False)

    def state(self):
        start = time.time()
        total_states = 0
        states_caught = 0
        while time.time() - start < BOUNCE_SEARCH:
            total_states = gpio.input(self.__pin)
            states_caught += 1
        avg = total_states / states_caught
        return round(avg)
