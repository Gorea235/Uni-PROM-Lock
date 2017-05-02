#! /usr/bin/env
__all__ = ["test_source"]

TMP_DIR = "tmp"


def test_source():
    # begin imports
    import unittest
    import os

    if not os.path.isdir(TMP_DIR):
        os.mkdir(TMP_DIR)
    os.chdir(TMP_DIR + "/")
    for f in os.listdir(TMP_DIR):
        ff = os.path.join(TMP_DIR, f)
        if os.path.isfile(ff):
            os.remove(ff)

    import sys
    sys.path.append("../src")
    sys.path.append("../lib")

    gpio_available = None
    try:
        import RPi.GPIO as gpio
        gpio_available = True
    except ImportError:
        gpio_available = False

    from . import test_code_lock
    if gpio_available:
        from . import test_gpio_wrapper
        from . import test_interface_wrapper
    from . import test_logger
    from . import test_timeout

    # init testing
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # load tests from modules to suite
    suite.addTests(loader.loadTestsFromModule(test_code_lock))
    if gpio_available:
        suite.addTests(loader.loadTestsFromModule(test_gpio_wrapper))
        suite.addTests(loader.loadTestsFromModule(test_interface_wrapper))
    suite.addTests(loader.loadTestsFromModule(test_logger))
    suite.addTests(loader.loadTestsFromModule(test_timeout))

    # init runner and begin testing
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    os.chdir("..")
    return result
