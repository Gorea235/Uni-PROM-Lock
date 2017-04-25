#! /usr/bin/env python

DEBUG = 3
NORMAL = 2
WARNING = 1
ERROR = 0

class Logger:
        @property
        def trace_level(self):
            return self.__trace_lvl
        
        @trace_level.setter
        def trace_level(self, value):
            assert isinstance(value, int)
            return self.__trace_lvl

        def __init__(self, log_path):
            self.__trace_lvl = NORMAL
            self.__out_file = open(log_path, mode='a')
        
        def __check_level(self, required):
            if required >= self.trace_level:
                return True
            return False

        def __write_log(self, level, line, *args):
            pass

        def logd(self, line, *args):
            pass
        
        def log(self, line, *args):
            pass
        
        def logw(self, line, *args):
            pass
        
        def loge(self, exception, msg="An exception occured, please talk to developer"):
            pass
