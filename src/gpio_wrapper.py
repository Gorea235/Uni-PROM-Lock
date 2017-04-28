#! /usr/bin/env python3
import RPi.GPIO as gpio
import time

HARDWARE_WAIT = 0.010

class GpioWrapper:
    def __init__(self, pin):
        self.__pin = pin

    def set(self, value):
        assert isinstance(value, bool)
        gpio.output(self.__pin, value)
        time.sleep(HARDWARE_WAIT)

    def high(self):
        self.set(True)

    def low(self):
        self.set(False)
