#! /usr/bin/env python3
import unittest
import timeout
import threading


class TimeoutTest(unittest.TestCase):
    def setUp(self):
        self.tm = timeout.Timeout(2)

    def tearDown(self):
        self.tm.cleanup()

    def test_init(self):
        self.assertTrue(isinstance(self.tm._timer, threading.Timer))
        self.assertEqual(self.tm._timer.interval, 2)
    
    def test_start(self):
        self.tm.start()
        self.assertTrue(self.tm.active)
    
    def test_reset(self):
        self.tm.start()
        self.tm.reset()
        self.assertFalse(self.tm.active)
    
    def test_restart(self):
        self.tm.start()
        self.tm.reset()
        self.assertTrue(self.tm.active)
    
    def test_active(self):
        self.assertEqual(self.tm.active, self.tm._timer.is_alive())
        self.tm.start()
        self.assertEqual(self.tm.active, self.tm._timer.is_alive())
    
    def test_cleanup(self):
        self.tm.start()
        self.tm.cleanup()
        self.assertFalse(self.tm.active)
