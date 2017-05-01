#! /usr/bin/env python3
import datetime

TRACE = 4
""""The trace tracing level"""
DEBUG = 3
"""The debug trace level"""
INFO = 2
"""The normal trace level"""
WARNING = 1
"""The warning trace level"""
ERROR = 0
"""The error trace level"""
_trace_names = {
    TRACE: "TRCE",
    DEBUG: "DBUG",
    INFO: "INFO",
    WARNING: "WARN",
    ERROR: "CRIT"
}


class Logger:
    @property
    def trace_level(self):
        return self._trace_lvl

    @trace_level.setter
    def trace_level(self, value):
        assert isinstance(value, int)
        self._trace_lvl = value

    @property
    def log_format(self):
        """The format of each write to the log,
        including the current trace level and current time of the log."""
        return self._log_fmt

    @log_format.setter
    def log_format(self, value):
        assert isinstance(value, str)
        self._log_fmt = value

    def __init__(self, log_path):
        self._trace_lvl = INFO
        self._log_fmt = "[{0}][{1:%Y-%m-%d}][{1:%H:%M:%S}] {2}"
        self._out_file = open(log_path, mode='a')

    def _check_level(self, required):
        if required <= self.trace_level:
            return True
        return False

    def _write_log(self, level, line, *args):
        if not self._check_level(level):
            return
        to_write = ""
        if len(args) == 0:
            to_write = line
        else:
            to_write = line.format(*args)
        self._out_file.write(self.log_format.format(
            _trace_names[level], datetime.datetime.now(), to_write) + "\n")
    
    def logt(self, line, *args):
        self._write_log(TRACE, line, *args)

    def logd(self, line, *args):
        self._write_log(DEBUG, line, *args)

    def log(self, line, *args):
        self._write_log(INFO, line, *args)

    def logw(self, line, *args):
        self._write_log(WARNING, line, *args)

    def loge(self, exception, msg="An exception occured, please talk to developer"):
        self._write_log(ERROR, "{0}\n{1}", msg, exception)

    def cleanup(self):
        self._out_file.close()
