#! /usr/bin/env python3
# this file will only contain limited testing due
# to the hardware-interaction nature of the module
import unittest
import gpio_wrapper


class GpioWrapperTest(unittest.TestCase):
    def test_init(self):
        gw = gpio_wrapper.GpioWrapper(10)
        self.assertEqual(gw._pin, 10)
        self.assertTrue(gw._io_inp)
