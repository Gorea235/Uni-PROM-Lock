#! /usr/bin/env
__all__ = ["test_source"]


def test_source():
    # begin imports
    import unittest

    import sys
    sys.path.append("../src")
    sys.path.append("../lib")

    from . import test_code_lock
    # from . import test_gpio_wrapper
    # from . import test_interface_wrapper
    from . import test_logger
    from . import test_stdout

    # init testing
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # load tests from modules to suite
    suite.addTests(loader.loadTestsFromModule(test_code_lock))
    # suite.addTests(loader.loadTestsFromModule(test_gpio_wrapper))
    # suite.addTests(loader.loadTestsFromModule(test_interface_wrapper))
    suite.addTests(loader.loadTestsFromModule(test_logger))
    suite.addTests(loader.loadTestsFromModule(test_stdout))

    # init runner and begin testing
    runner = unittest.TextTestRunner()
    return runner.run(suite)
