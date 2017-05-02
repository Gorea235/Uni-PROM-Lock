#! /usr/bin/env python3
import unittest
import timeout
import threading
import time


class TimeoutTest(unittest.TestCase):
    def setUp(self):
        self.tm = timeout.Timeout(1)

    def tearDown(self):
        self.tm.cleanup()

    def test_init(self):
        self.assertTrue(isinstance(self.tm._timer, threading.Timer))
        self.assertEqual(self.tm._timer.interval, 1)
    
    def test_start(self):
        self.tm.start()
        self.assertTrue(self.tm.active)
        self.tm.reset()
        time.sleep(0.001)
        self.assertFalse(self.tm.active)
        self.tm.start()
        self.assertTrue(self.tm.active)

    def fired_tester_func(self):
        self.fired = True

    def test_fired(self):
        self.fired = False
        self.tm.elapsed.bind(self.fired_tester_func)
        self.tm.start()
        time.sleep(0.9)
        self.assertFalse(self.fired)
        time.sleep(0.11)
        self.assertTrue(self.fired)
    
    def test_reset(self):
        self.tm.start()
        self.tm.reset()
        time.sleep(0.001)
        self.assertFalse(self.tm.active)
    
    def test_restart(self):
        self.tm.start()
        self.tm.restart()
        time.sleep(0.001)
        self.assertTrue(self.tm.active)
    
    def test_active(self):
        self.assertEqual(self.tm.active, self.tm._timer.is_alive())
        self.tm.start()
        self.assertEqual(self.tm.active, self.tm._timer.is_alive())
    
    def test_cleanup(self):
        self.tm.start()
        self.tm.cleanup()
        time.sleep(0.001)
        self.assertFalse(self.tm.active)
