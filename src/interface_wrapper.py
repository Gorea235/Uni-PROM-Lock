#! /usr/bin/env python

class InterfaceWrapper:
    """
    The main class used by the startup to handle the interfacing.
    """

    def __init__(self, logger):
        pass

    def main_loop(self):
        """
        Starts up the main loop of the interface, loop is wrapped in an exception handler that can handle both ‘Exception’ and ‘KeyboardInterrupt’.
        """
        pass
    
    def cleanup(self):
        """
        Cleans up any variables before exit.
        """
        pass
    
    def flash_green_led(self):
        """
        Causes the green LED to flash once (if mid-flash, it will either do nothing or just reset the duration left on the flash, depending on how the hardware works).
        """
        pass
    
    def flash_red_led(self):
        """
        Causes the red LED to flash once (if mid-flash, it will either do nothing or just reset the duration left on the flash, depending on how the hardware works).
        """
        pass
    
    def beep_buzzer(self):
        """
        Causes the buzzer to go off once (if it is already buzzing, it will either do nothing or just reset the duration left on the buzz, depending on how the hardware works).
        """
        pass
