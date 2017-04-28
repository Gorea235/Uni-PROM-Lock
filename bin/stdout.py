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
        self.__second_pass = False

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
            if not self.__second_pass:
                self.__clear_line()
                self.__owrite(s)
                self.__second_pass = True
            else:
                self.__owrite(s)
                self.__dsp_overwrite_line()
                self.__second_pass = False
        else:
            self.__owrite(s)
    
    def flush(self):
        self.__old_stdout.flush()

    def __owrite(self, s):
        self.__old_stdout.write(s)
    
    def __clear_line(self):
        self.__owrite("\r" + (" " * 40) + "\r")
    
    def __dsp_overwrite_line(self):
        self.__clear_line()
        self.__owrite(self.overwrite_text)
        self.flush()

    def start_overwrite_output(self):
        """
        Starts an overwritten output that will be replaced on each write instead of appended to.
        """
        if self.__overwrite_enabled:
            return
        self.flush()
        self.__overwrite_enabled = True
        self.__overwrite_text = ""
    
    def end_overwrite_output(self):
        """
        Stops the overwritten output and returns the printed lines to a reasonable state.
        """
        if not self.__overwrite_enabled:
            return
        self.__owrite("\n")
        self.__overwrite_enabled = False
    
    def cleanup(self):
        self.end_overwrite_output()
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

##for i in range(10):
##    sys.stdout.write("\r" + "{}".format(i)*i)
##    sys.stdout.flush()
##    time.sleep(0.5)
