#! /usr/bin/env python3
import unittest
from .lib_test import *
import interface_wrapper
import RPi.GPIO as gpio
import event


class GpioWrapper_Test:
    def __init__(self, pin):
        self._pin = pin
        self._io_inp = True
        self._mode = None
        self._output = False
        self._check_state = 0
        self.input()

    @staticmethod
    def set_multiple_output(*args):
        for t in args:
            t[0]._apply_output(t[1])

    def set_io(self, state):
        self._mode = state

    def input(self):
        self.set_io(gpio.IN)

    def output(self):
        self.set_io(gpio.OUT)

    def set_output(self, value):
        self._apply_output(value)

    def _apply_output(self, value):
        assert isinstance(value, bool)
        self._output = value

    def high(self):
        self.set_output(True)

    def low(self):
        self.set_output(False)

    def state(self):
        return self._check_state

    @property
    def is_high(self):
        return self.state() == 1

    @property
    def is_low(self):
        return self.state() == 0


interface_wrapper.GpioWrapper = GpioWrapper_Test


class InterfaceWrapperTest(unittest.TestCase):
    _rcv_digit = None

    def setUp(self):
        self.log = Logger_Test()
        self.iface = interface_wrapper.InterfaceWrapper(self.log)

    def tearDown(self):
        self.iface.cleanup()

    def test_init(self):
        self.assertTrue(isinstance(self.iface.digit_received, event.Event))
        self.assertTrue(self.iface._run_loop)
        self.assertEqual(self.iface._current_digit, 0)
        self.assertFalse(self.iface._digit_down)
        self.assertFalse(self.iface._led_green_apply)
        self.assertFalse(self.iface._led_red_apply)
        self.assertFalse(self.iface._buzzer_apply)

        self.assertEqual(self.iface.gpio.reg._mode, gpio.OUT)
        self.assertEqual(self.iface.gpio.io._mode, gpio.OUT)

    def test_start_read(self):
        self.iface._start_read()
        self.assertFalse(self.iface.gpio.reg._output)
        self.assertEqual(self.iface.gpio._lines["d0"]._mode, gpio.IN)
        self.assertEqual(self.iface.gpio._lines["d1"]._mode, gpio.IN)
        self.assertEqual(self.iface.gpio._lines["d2"]._mode, gpio.IN)
        self.assertTrue(self.iface.gpio.io._output)

    def fired_test(self, digit):
        self.fired = True
        self._rcv_digit = digit

    def test_do_read_phase(self):
        self.iface.digit_received.bind(self.fired_test)
        self.fired = False
        self.iface.gpio._lines["d0"]._check_state = True
        self.iface.gpio._lines["d1"]._check_state = True
        self.iface.gpio._lines["d2"]._check_state = True
        self.iface._do_read_phase()
        self.assertFalse(self.fired)
        self.iface._do_read_phase()
        self.assertFalse(self.fired)

        self.iface.gpio._lines["d0"]._check_state = False
        self.iface._do_read_phase()
        self.assertTrue(self.fired)
        self.assertEqual(self._rcv_digit, "1")

        self.fired = False
        self._rcv_digit = None
        self.iface._do_read_phase()
        self.assertFalse(self.fired)

        self.iface.gpio._lines["d0"]._check_state = True
        self.iface._do_read_phase()
        self.assertFalse(self.iface._digit_down)
        self.assertFalse(self.fired)

        self.iface.gpio._lines["d1"]._check_state = False
        self.iface._do_read_phase()
        self.assertTrue(self.fired)
        self.assertEqual(self._rcv_digit, "2")

        self.fired = False
        self._rcv_digit = None
        self.iface._do_read_phase()
        self.assertFalse(self.fired)

        self.iface.gpio._lines["d1"]._check_state = True
        self.iface._do_read_phase()
        self.assertFalse(self.iface._digit_down)
        self.assertFalse(self.fired)

        self.iface._current_digit = 1
        self.iface.gpio._lines["d0"]._check_state = False
        self.iface._do_read_phase()
        self.assertTrue(self.fired)
        self.assertEqual(self._rcv_digit, "4")

        self.fired = False
        self._rcv_digit = None
        self.iface._do_read_phase()
        self.assertFalse(self.fired)

        self.iface.gpio._lines["d0"]._check_state = True
        self.iface._do_read_phase()
        self.assertFalse(self.iface._digit_down)
        self.assertFalse(self.fired)

    def test_start_write(self):
        self.iface._start_write()
        self.assertTrue(self.iface.gpio.reg._output)
        self.assertEqual(self.iface.gpio._lines["d0"]._mode, gpio.OUT)
        self.assertEqual(self.iface.gpio._lines["d1"]._mode, gpio.OUT)
        self.assertEqual(self.iface.gpio._lines["d2"]._mode, gpio.OUT)
        self.assertFalse(self.iface.gpio.io._output)

    def get_digit_output(self):
        return [self.iface.gpio._lines["d2"]._output,
               self.iface.gpio._lines["d1"]._output,
               self.iface.gpio._lines["d0"]._output]

    def test_do_write_phase(self):
        self.iface._do_write_phase()
        self.assertEqual(self.get_digit_output(), [False, False, False])
        self.iface._do_write_phase()
        self.assertEqual(self.get_digit_output(), [False, False, True])
        self.iface._do_write_phase()
        self.assertEqual(self.get_digit_output(), [False, True, False])
        self.iface._do_write_phase()
        self.assertEqual(self.get_digit_output(), [False, True, True])

        self.iface.flash_green_led()
        self.iface._do_write_phase()
        self.assertEqual(self.get_digit_output(), [True, False, False])
        self.assertFalse(self.iface._led_green_apply)

        self.iface.flash_red_led()
        self.iface._do_write_phase()
        self.assertEqual(self.get_digit_output(), [True, False, True])
        self.assertFalse(self.iface._led_red_apply)

        self.iface.beep_buzzer()
        self.iface._do_write_phase()
        self.assertEqual(self.get_digit_output(), [True, True, False])
        self.assertFalse(self.iface._buzzer_apply)

    def test_cleanup(self):
        self.iface.cleanup()
        self.assertFalse(self.iface._run_loop)

    def test_flash_green_led(self):
        self.iface.flash_green_led()
        self.assertTrue(self.iface._led_green_apply)

    def test_flash_red_led(self):
        self.iface.flash_red_led()
        self.assertTrue(self.iface._led_red_apply)

    def test_beep_buzzer(self):
        self.iface.beep_buzzer()
        self.assertTrue(self.iface._buzzer_apply)
