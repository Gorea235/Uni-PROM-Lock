#! /usr/bin/env python3
# this file will only contain limited testing due
# to the hardware-interaction nature of the module
import unittest
import gpio_wrapper
import RPi.GPIO as gpio


class GpioWrapperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
    
    def test_init(self):
        gw = gpio_wrapper.GpioWrapper(10)
        self.assertEqual(gw._pin, 10)
        self.assertTrue(gw._io_inp)
