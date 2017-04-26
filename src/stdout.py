import sys

class StdoutOverwrite:
    """
    The standard output for the system. The write method will replace the sys.stdout.write method, but still use it.
    """

    def __init__(self):
        self.__old_stdout = sys.stdout
        sys.stdout = self
        self.__overwrite_enabled = False
        self.__overwrite_text = ""

    @property
    def overwrite_text(self):
        """
        Sets/gets the current output of the written line.
        """
        return self.__overwrite_text
    
    @overwrite_text.setter
    def overwrite_text(self, value):
        assert isinstance(value, str)
        self.__overwrite_text = value
        self.__dsp_overwrite_line()
    
    def write(self, s):
        """
        Writes a line to stdout.
        """
        if self.__overwrite_enabled:
            self.__clear_line()
            self.__old_stdout.write(s)
            self.__dsp_overwrite_line()
        else:
            self.__old_stdout.write(s)
    
    def flush(self):
        self.__old_stdout.flush()
    
    def __clear_line(self):
        self.__old_stdout.write("\r" + (" " * 40) + "\r")
        self.flush()
    
    def __dsp_overwrite_line(self):
        self.__clear_line()
        self.__old_stdout.write(self.overwrite_text)
        self.flush()

    def start_overwrite_output(self):
        """
        Starts an overwritten output that will be replaced on each write instead of appended to.
        """
        if self.__overwrite_enabled:
            return
        self.__old_stdout.write("\n")
        self.flush()
        self.__overwrite_enabled = True
    
    def end_overwrite_output(self):
        """
        Stops the overwritten output and returns the printed lines to a reasonable state.
        """
        if not self.__overwrite_enabled:
            return
        self.__old_stdout.write("\n")
        self.__overwrite_enabled = False
    
    def cleanup(self):
        sys.stdout = self.__old_stdout

if __name__ == "__main__":
    import time
    out = StdoutOverwrite()
    wait = 0.5
    print("begin")
    out.start_overwrite_output()
    out.overwrite_text = "a"
    time.sleep(wait)
    out.overwrite_text = "bcd"
    time.sleep(wait)
    out.overwrite_text = "x"
    time.sleep(wait)
    out.end_overwrite_output()
    print("hello")
    time.sleep(wait)
    print("world")
    time.sleep(wait)
    out.start_overwrite_output()
    print("testing")
    time.sleep(wait)
    out.overwrite_text = "*"
    time.sleep(wait)
    print("testing again")
    time.sleep(wait)
    out.overwrite_text = "**"
    time.sleep(wait)
    out.overwrite_text = "*"
    time.sleep(wait)
    out.overwrite_text = "*****"
    time.sleep(wait)
    print("test")
    time.sleep(wait)
    out.overwrite_text = "123"
    time.sleep(wait)
    print("final")
    time.sleep(wait)
    out.end_overwrite_output()
    print("end")
    time.sleep(wait)
    print("test")
    time.sleep(wait)
    out.start_overwrite_output()
    out.overwrite_text = "1234"
    time.sleep(wait)
    out.overwrite_text = "12"
    time.sleep(wait)
    out.end_overwrite_output()
    out.cleanup()
