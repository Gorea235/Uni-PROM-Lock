#! /usr/bin/env python3
import unittest
import logger
import io
import datetime

TMP_LOG = "test.log"


class LoggerTest(unittest.TestCase):
    def get_logger(self):
        log = logger.Logger(TMP_LOG)
        log._out_file.close()
        log._out_file = io.StringIO()
        return log

    def getcontents(self, log):
        log._out_file.flush()
        log._out_file.seek(0)
        return log._out_file.read()

    def getlength(self, log):
        return len(self.getcontents(log))

    def clearcontents(self, log):
        log._out_file.flush()
        log._out_file.seek(0)
        log._out_file.truncate()

    def test_init(self):
        log = logger.Logger(TMP_LOG)
        self.assertTrue(isinstance(log.trace_level, int))
        self.assertEqual(log.trace_level, logger.INFO)
        self.assertTrue(isinstance(log.log_format, str))
        self.assertTrue(isinstance(log._out_file, io.IOBase))

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
        self.assertRegex(self.getcontents(
            log), "\\AINFO {:%Y-%m-%d} test\\n\\Z".format(cdt))
        cdt2 = datetime.datetime.now()
        log.logw("test2")
        self.assertRegex(self.getcontents(
            log), "\\AINFO {:%Y-%m-%d} test\\nWARN {:%Y-%m-%d} test2\\n\\Z".format(cdt, cdt2))

    def test_logt(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        log.logt("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.DEBUG
        log.logt("test")
        self.assertEqual(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.INFO
        log.logt("test")
        self.assertEqual(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.WARNING
        log.logt("test")
        self.assertEqual(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.ERROR
        log.logt("test")
        self.assertEqual(self.getlength(log), 0)

    def test_logd(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        log.logd("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.DEBUG
        log.logd("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.INFO
        log.logd("test")
        self.assertEqual(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.WARNING
        log.logd("test")
        self.assertEqual(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.ERROR
        log.logd("test")
        self.assertEqual(self.getlength(log), 0)

    def test_log(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        log.log("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.DEBUG
        log.log("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.INFO
        log.log("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.WARNING
        log.log("test")
        self.assertEqual(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.ERROR
        log.log("test")
        self.assertEqual(self.getlength(log), 0)

    def test_multi_log(self):
        log = self.get_logger()
        log.log("test")
        clen = self.getlength(log)
        self.assertGreater(clen, 0)
        log.logw("test2")
        tlen = self.getlength(log)
        self.assertGreater(tlen, clen)
        self.clearcontents(log)
        log.log("test")
        log.logw("test2")
        self.assertEqual(self.getlength(log), tlen)

    def test_logw(self):
        log = self.get_logger()
        log.trace_level = logger.TRACE
        log.logw("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.DEBUG
        log.logw("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.INFO
        log.logw("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.WARNING
        log.logw("test")
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.ERROR
        log.logw("test")
        self.assertEqual(self.getlength(log), 0)

    def test_loge(self):
        log = self.get_logger()
        ex = Exception()
        log.trace_level = logger.TRACE
        log.loge(ex)
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.DEBUG
        log.loge(ex)
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.INFO
        log.loge(ex)
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.WARNING
        log.loge(ex)
        self.assertGreater(self.getlength(log), 0)
        self.clearcontents(log)
        log.trace_level = logger.ERROR
        log.loge(ex)
        self.assertGreater(self.getlength(log), 0)

    def test_cleanup(self):
        log = logger.Logger(TMP_LOG)
        log.cleanup()
        self.assertRaises(ValueError, log.log, "test log")
