#! /usr/bin/env python3
import unittest
from .lib_test import *
import code_lock
import timeout
import os
import datetime


class CodeLockTest(unittest.TestCase):
    def get_code_lock(self):
        iface = InferfaceWrapper_Test()
        log = Logger_Test()
        stdout = Stdout_Test()
        main = Main_Test()
        return code_lock.CodeLock(iface, log, stdout, main), iface, log, stdout, main

    def get_file_contents(self, f):
        f.flush()
        f.seek(0)
        return f.read()

    def get_file_length(self, f):
        return len(self.get_file_contents(f))

    def setUpClass(self):
        self.store_TIME_LOCKOUT_BEGIN = code_lock.TIME_LOCKOUT_BEGIN
        self.store_TIME_LOCKOUT_END = code_lock.TIME_LOCKOUT_END
        self.store_IMMEDIATE_REJECT = code_lock.IMMEDIATE_REJECT
        self._datetime = datetime.datetime.now

    def setUp(self):
        self.clk, self.iface, self.log, self.stdout, self.main = self.get_code_lock()

    def tearDown(self):
        self.clk.cleanup()
        for c in self.main.wrapped:
            c.cleanup()
        code_lock.TIME_LOCKOUT_BEGIN = self.store_TIME_LOCKOUT_BEGIN
        code_lock.TIME_LOCKOUT_END = self.store_TIME_LOCKOUT_END
        code_lock.IMMEDIATE_REJECT = self.store_IMMEDIATE_REJECT

    def test_init(self):
        self.assertEqual(self.clk.iface, self.iface)
        self.assertEqual(self.clk.logger, self.log)
        self.assertEqual(self.clk.stdout, self.stdout)

        self.assertGreater(len(self.iface.digit_received._event_funcs), 0)
        self.assertTrue(isinstance(self.clk.digit_timeout, timeout.Timeout))
        self.assertEqual(self.clk.digit_timeout._timer.interval, 3)

        self.assertEqual(self.clk.password, ["1", "2", "3", "4"])
        self.assertTrue(os.path.isfile("password.txt"))
        with open("password.txt") as f:
            self.assertEqual(f.read().strip(), "1234")

        self.assertTrue(isinstance(self.clk.access_log, io.IOBase))
        self.assertGreater(self.get_file_length(self.clk.access_log), 0)

        self.assertEqual(self.clk.current_input, [])
        self.assertEqual(self.clk.locked_out, False)
        self.assertTrue(isinstance(self.clk.locked_timeout, timeout.Timeout))
        self.assertEqual(self.clk.locked_timeout._timer.interval, 1)
        self.assertEqual(self.clk.incorrect_attempts, 0)
        self.assertEqual(self.clk.locked_time_left, 0)

        self.assertEqual(len(self.main.wrapped), 2)

    def test_access_log_append(self):
        l = self.get_file_length(self.clk.access_log)
        self.clk.access_log_append("event", True)
        self.clk.access_log.flush()
        self.clk.access_log.seek(l)
        self.assertRegex(self.clk.access_log.read(),
                         r"^event,\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d,True\n$")
        l = self.get_file_length(self.clk.access_log)
        self.clk.access_log_append("event2", False)
        self.clk.access_log.flush()
        self.clk.access_log.seek(l)
        self.assertRegex(self.clk.access_log.read(),
                         r"^event2,\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d,False\n$")

    def test_password_entered(self):
        self.clk.password_entered(False, False)
        self.assertRegex(self.get_file_contents(
            self.clk.access_log), r"False$")
        self.assertEqual(self.clk.incorrect_attempts, 0)
        self.assertTrue(self.iface.led_red_flashed)
        self.iface.led_red_flashed = False
        self.clk.password_entered(False)
        self.assertEqual(self.clk.incorrect_attempts, 1)
        self.assertTrue(self.iface.led_red_flashed)
        self.iface.led_red_flashed = False
        self.clk.password_entered(True)
        self.assertEqual(self.clk.incorrect_attempts, 0)
        self.assertTrue(self.iface.led_green_flashed)
        for i in range(5):
            self.clk.password_entered(False)
            self.assertEqual(self.clk.incorrect_attempts, i)
        self.assertTrue(self.clk.locked_timeout.active)
        self.clk.locked_timeout.reset()

    def test_lockout(self):
        self.clk.incorrect_attempts = 3
        self.clk.lockout()
        self.assertTrue(self.clk.locked_timeout.active)
        self.clk.locked_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 0)
        self.assertTrue(self.clk.locked_out)
        self.assertEqual(self.clk.locked_time_left, code_lock.LOCKED_OUT_TIME)

    def test_locked_timeout_elapsed(self):
        test_time = 10
        self.clk.locked_time_left = test_time
        self.clk.locked_out = True
        for i in range(1, test_time + 1):
            self.clk.locked_timeout_elapsed()
            self.assertEqual(self.clk.locked_time_left, test_time - i)
            if i < test_time:
                self.assertTrue(self.clk.locked_timeout.active)
                self.clk.locked_timeout.reset()
            else:
                self.assertFalse(self.clk.locked_timeout.active)
                self.assertFalse(self.clk.locked_out)

    def test_digit_received_handler(self):
        self.clk.locked_out = True
        code_lock.TIME_LOCKOUT_BEGIN = (0, 0)
        code_lock.TIME_LOCKOUT_END = (0, 0)
        self.clk.digit_received_handler("1")
        self.assertFalse(self.iface.buzzer_enabled)
        self.clk.locked_out = False

        cdt = datetime.datetime.now()
        tdt = cdt + datetime.timedelta(minutes=2)
        code_lock.TIME_LOCKOUT_BEGIN = datetime.time(tdt.hour, tdt.minute)
        tdt = cdt + datetime.timedelta(minutes=12)
        code_lock.TIME_LOCKOUT_END = datetime.time(tdt.hour, tdt.minute)
        self.clk.digit_received_handler("1")
        self.assertFalse(self.iface.buzzer_enabled)

        cdt = datetime.datetime.now()
        tdt = cdt + datetime.timedelta(hours=2)
        code_lock.TIME_LOCKOUT_BEGIN = datetime.time(tdt.hour, tdt.minute)
        tdt = cdt + datetime.timedelta(hours=4)
        code_lock.TIME_LOCKOUT_END = datetime.time(tdt.hour, tdt.minute)
        self.clk.digit_received_handler("1")
        self.assertFalse(self.iface.buzzer_enabled)

        cdt = datetime.datetime.now()
        tdt = cdt + datetime.timedelta(minutes=-12)
        code_lock.TIME_LOCKOUT_BEGIN = datetime.time(tdt.hour, tdt.minute)
        tdt = cdt + datetime.timedelta(minutes=-2)
        code_lock.TIME_LOCKOUT_END = datetime.time(tdt.hour, tdt.minute)
        self.clk.digit_received_handler("1")
        self.assertFalse(self.iface.buzzer_enabled)

        cdt = datetime.datetime.now()
        tdt = cdt + datetime.timedelta(hours=-4)
        code_lock.TIME_LOCKOUT_BEGIN = datetime.time(tdt.hour, tdt.minute)
        tdt = cdt + datetime.timedelta(hours=-2)
        code_lock.TIME_LOCKOUT_END = datetime.time(tdt.hour, tdt.minute)
        self.clk.digit_received_handler("1")
        self.assertFalse(self.iface.buzzer_enabled)

    def test_digit_received_handler_time_dep_succ_min(self):
        cdt = datetime.datetime.now()
        code_lock.TIME_LOCKOUT_BEGIN = datetime.time(cdt.hour, cdt.minute)
        tdt = cdt + datetime.timedelta(minutes=1)
        code_lock.TIME_LOCKOUT_END = datetime.time(tdt.hour, tdt.minute)
        self.assertTrue(self.iface.buzzer_enabled)

    def test_digit_received_handler_time_dep_succ_hour(self):
        cdt = datetime.datetime.now()
        code_lock.TIME_LOCKOUT_BEGIN = datetime.time(cdt.hour, cdt.minute)
        tdt = cdt + datetime.timedelta(hours=1)
        code_lock.TIME_LOCKOUT_END = datetime.time(tdt.hour, tdt.minute)
        self.assertTrue(self.iface.buzzer_enabled)

    def test_digit_received_handler_time_dep_succ_0(self):
        code_lock.TIME_LOCKOUT_BEGIN = datetime.time(0, 0)
        code_lock.TIME_LOCKOUT_END = datetime.time(0, 0)
        self.assertTrue(self.iface.buzzer_enabled)

    def test_digit_received_handler_time_dep_succ_1(self):
        code_lock.TIME_LOCKOUT_BEGIN = datetime.time(1, 1)
        code_lock.TIME_LOCKOUT_END = datetime.time(1, 1)
        self.assertTrue(self.iface.buzzer_enabled)

    def test_digit_received_handler_password_incorrect_1a(self):
        self.clk.digit_received_handler("1")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1"])
        self.clk.digit_received_handler("2")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2"])
        self.clk.digit_received_handler("3")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2", "3"])
        self.clk.digit_received_handler("5")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 1)
        self.assertTrue(self.iface.led_red_flashed)
        self.assertEqual(self.clk.current_input, [])

    def test_digit_received_handler_password_incorrect_2a(self):
        self.clk.digit_received_handler("1")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1"])
        self.clk.digit_received_handler("4")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "4"])
        self.clk.digit_received_handler("3")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "4", "3"])
        self.clk.digit_received_handler("4")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 1)
        self.assertTrue(self.iface.led_red_flashed)
        self.assertEqual(self.clk.current_input, [])

    def test_digit_received_handler_password_incorrect_3a(self):
        self.clk.digit_received_handler("4")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["4"])
        self.clk.digit_received_handler("3")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["4", "3"])
        self.clk.digit_received_handler("2")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["4", "3", "2"])
        self.clk.digit_received_handler("1")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 1)
        self.assertTrue(self.iface.led_red_flashed)
        self.assertEqual(self.clk.current_input, [])

    def test_digit_received_handler_password_incorrect_1b(self):
        code_lock.IMMEDIATE_REJECT = True
        self.clk.digit_received_handler("1")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1"])
        self.clk.digit_received_handler("2")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2"])
        self.clk.digit_received_handler("3")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2", "3"])
        self.clk.digit_received_handler("5")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 1)
        self.assertTrue(self.iface.led_red_flashed)
        self.assertEqual(self.clk.current_input, [])

    def test_digit_received_handler_password_incorrect_2b(self):
        code_lock.IMMEDIATE_REJECT = True
        self.clk.digit_received_handler("1")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1"])
        self.clk.digit_received_handler("2")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2"])
        self.clk.digit_received_handler("4")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 1)
        self.assertTrue(self.iface.led_red_flashed)
        self.assertEqual(self.clk.current_input, [])

    def test_digit_received_handler_password_incorrect_3b(self):
        code_lock.IMMEDIATE_REJECT = True
        self.clk.digit_received_handler("1")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1"])
        self.clk.digit_received_handler("3")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 1)
        self.assertTrue(self.iface.led_red_flashed)
        self.assertEqual(self.clk.current_input, [])

    def test_digit_received_handler_password_correct_a(self):
        self.clk.digit_received_handler("1")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1"])
        self.clk.digit_received_handler("2")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2"])
        self.clk.digit_received_handler("3")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2", "3"])
        self.clk.digit_received_handler("4")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 0)
        self.assertTrue(self.iface.led_green_flashed)
        self.assertEqual(self.clk.current_input, [])

    def test_digit_received_handler_password_correct_b(self):
        code_lock.IMMEDIATE_REJECT = True
        self.clk.digit_received_handler("1")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1"])
        self.clk.digit_received_handler("2")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2"])
        self.clk.digit_received_handler("3")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.current_input, ["1", "2", "3"])
        self.clk.digit_received_handler("4")
        self.clk.digit_timeout.reset()
        self.assertEqual(self.clk.incorrect_attempts, 0)
        self.assertTrue(self.iface.led_green_flashed)
        self.assertEqual(self.clk.current_input, [])

    def test_digit_timeout_elapsed(self):
        self.clk.digit_timeout_elapsed()
        self.assertTrue(self.iface.led_red_flashed)
        self.assertEqual(self.clk.incorrect_attempts, 0)

    def test_cleanup(self):
        self.assertFalse(self.clk.digit_timeout.active)
        self.assertFalse(self.clk.locked_timeout.active)
        self.assertTrue(self.clk.access_log.closed)
