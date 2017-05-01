#! /usr/bin/env python3
import unittest
import logger
import io
import datetime

TMP_LOG = "test.log"


class LoggerTest(unittest.TestCase):
    def get_logger(self):
        log = logger.Logger(TMP_LOG)
        log._Logger__out_file.close()
        log._Logger__out_file = io.StringIO()
        return log

    def get_logger_contents(self, log):
        log._Logger__out_file.flush()
        log._Logger__out_file.seek(0)
        return log._Logger__out_file.read()

    def get_logger_length(self, log):
        return len(self.get_logger_contents(log))

    def clear_logger_contents(self, log):
        log._Logger__out_file.flush()
        log._Logger__out_file.seek(0)
        log._Logger__out_file.truncate()

    def test_init(self):
        log = logger.Logger(TMP_LOG)
        self.assertTrue(isinstance(log.trace_level, int))
        self.assertEqual(log.trace_level, logger.INFO)
        self.assertTrue(isinstance(log.log_format, str))
        self.assertTrue(isinstance(log._Logger__out_file, io.IOBase))

    def test_trace_level(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        self.assertEqual(log.trace_level, logger.TRACE)
        log.trace_level = logger.DEBUG
        self.assertEqual(log.trace_level, logger.DEBUG)
        log.trace_level = logger.INFO
        self.assertEqual(log.trace_level, logger.INFO)
        log.trace_level = logger.WARNING
        self.assertEqual(log.trace_level, logger.WARNING)
        log.trace_level = logger.ERROR
        self.assertEqual(log.trace_level, logger.ERROR)

    def test_log_format(self):
        log = self.get_logger()
        fmt = "testing format"
        log.log_format = fmt
        self.assertEqual(log.log_format, fmt)
        fmt = "{0} {1:%Y-%m-%d} {2}"
        log.log_format = fmt
        cdt = datetime.datetime.now()
        log.log("test")
        self.assertRegex(self.get_logger_contents(
            log), "\\AINFO {:%Y-%m-%d} test\\n\\Z".format(cdt))
        cdt2 = datetime.datetime.now()
        log.logw("test2")
        self.assertRegex(self.get_logger_contents(
            log), "\\AINFO {:%Y-%m-%d} test\\nWARN {:%Y-%m-%d} test2\\n\\Z".format(cdt, cdt2))

    def test_logt(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        log.logt("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.DEBUG
        log.logt("test")
        self.assertEqual(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.INFO
        log.logt("test")
        self.assertEqual(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.WARNING
        log.logt("test")
        self.assertEqual(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.ERROR
        log.logt("test")
        self.assertEqual(self.get_logger_length(log), 0)

    def test_logd(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        log.logd("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.DEBUG
        log.logd("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.INFO
        log.logd("test")
        self.assertEqual(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.WARNING
        log.logd("test")
        self.assertEqual(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.ERROR
        log.logd("test")
        self.assertEqual(self.get_logger_length(log), 0)

    def test_log(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        log.log("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.DEBUG
        log.log("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.INFO
        log.log("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.WARNING
        log.log("test")
        self.assertEqual(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.ERROR
        log.log("test")
        self.assertEqual(self.get_logger_length(log), 0)

    def test_multi_log(self):
        log = self.get_logger()
        log.log("test")
        clen = self.get_logger_length(log)
        self.assertGreater(clen, 0)
        log.logw("test2")
        tlen = self.get_logger_length(log)
        self.assertGreater(tlen, clen)
        self.clear_logger_contents(log)
        log.log("test")
        log.logw("test2")
        self.assertEqual(self.get_logger_length(log), tlen)

    def test_logw(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        log.logw("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.DEBUG
        log.logw("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.INFO
        log.logw("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.WARNING
        log.logw("test")
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.ERROR
        log.logw("test")
        self.assertEqual(self.get_logger_length(log), 0)

    def test_loge(self):
        log = self.get_logger()
        ex = Exception()
        log.trace_level = logger.TRACE
        log.loge(ex)
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.DEBUG
        log.loge(ex)
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.INFO
        log.loge(ex)
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.WARNING
        log.loge(ex)
        self.assertGreater(self.get_logger_length(log), 0)
        self.clear_logger_contents(log)
        log.trace_level = logger.ERROR
        log.loge(ex)
        self.assertGreater(self.get_logger_length(log), 0)

    def test_cleanup(self):
        log = logger.Logger(TMP_LOG)
        log.cleanup()
        self.assertRaises(ValueError, log.log, "test log")
