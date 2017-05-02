#! /usr/bin/env python3
import datetime
import os
from timeout import *

PWORD_FILE = "password.txt"
ACCESS_LOG_FILE = "access_log.csv"
DEFAULT_PWORD = "1234"
IMMEDIATE_REJECT = False
LOCKED_OUT_TIME = 60
# if the following values are different, then the lock will only allow attempts
# between the times
TIME_LOCKOUT_BEGIN = datetime.time(13, 0)  # hour, minute
TIME_LOCKOUT_END = datetime.time(14, 0)  # hour, minute
MAX_ATTEMPTS = 5


class CodeLock:
    def __init__(self, iface, logger, stdout):
        self.iface = iface  # store interface wrapper
        self.logger = logger  # store logger
        self.stdout = stdout  # store standard output

        # bind to digit recevied event
        self.iface.digit_received.bind(self.digit_received_handler)
        self.digit_timeout = Timeout(3)  # the digit timeout

        self.password = []  # password store
        if os.path.isfile(PWORD_FILE):  # file exists, read and use
            with open(PWORD_FILE) as f:
                self.password = f.read().strip()  # reads and cleans up
            self.logger.log("password read as {}", self.password)
        else:
            self.password = DEFAULT_PWORD  # use default password
            self.logger.log("password defaulted to {}", self.password)
            with open(PWORD_FILE, "w") as f:
                f.write(self.password)  # write new password.txt
            self.logger.log("wrote new password file to {}", PWORD_FILE)

        self.access_log = open(ACCESS_LOG_FILE, "a+")
        self.access_log_append("startup", None)

        self.current_input = []  # current digit input
        self.locked_out = False  # whether the user is locked out
        # the locked out timeout (supposed to go from 59-0, but should output
        # each second)
        self.locked_timeout = Timeout(1)
        self.incorrect_attempts = 0  # the number of incorrect attempts
        self.locked_time_left = 0  # the amount of time left for the user to be locked out

    def access_log_append(self, event_name, success):
        self.access_log.write(
            "{},{:%Y-%m-%dT%H:%M:%S},{}\n".format(event_name, datetime.datetime.now(), success))

    def password_entered(self, correct, count_attempt=True):
        """
        Resets digit timeout and stores the time of entry. Also handles the attempts count and LEDs.
        """
        self.digit_timeout.reset()
        self.current_input = []
        self.access_log_append("code", correct)
        if correct:
            self.incorrect_attempts = 0
            self.iface.flash_green_led()
            self.logger.log("password correct, attempts reset and LED pulsed")
        else:
            if count_attempt:
                self.incorrect_attempts += 1
            self.iface.flash_red_led()
            if self.incorrect_attempts == MAX_ATTEMPTS:
                self.lockout()
            self.logger.log("password incorrect, attempts: {}, LED pulsed".format(
                self.incorrect_attempts))

    def lockout(self):
        """
        Sets the user to be locked out
        """
        self.incorrect_attempts = 0
        self.locked_out = True
        self.locked_time_left = LOCKED_OUT_TIME
        self.locked_timeout.start()
        self.logger.log("user locked out, beginning countdown")

    def locked_timeout_elapsed(self):
        """
        Handles the elapsed event of the lockout timeout.
        """
        self.locked_time_left -= 1
        self.logger.logd(
            "locked out time left: {}".format(self.locked_time_left))
        self.stdout.overwrite_text = str(self.locked_time_left)
        if self.locked_time_left <= 0:
            self.locked_out = False
            self.logger.log("locked timeout finished, disabling")
        else:
            self.locked_timeout.start()
            self.logger.logd("restarted timeout second counter")

    def digit_received_handler(self, digit):
        """
        Handles the event when the user inputs a digit into the keypad.
        """
        self.logger.log("received digit '{}'".format(digit))
        if self.locked_out:
            self.logger.log("locked out, ignoring digit")
            return
        if TIME_LOCKOUT_BEGIN != TIME_LOCKOUT_END:
            now = datetime.datetime.now().time()
            if not (TIME_LOCKOUT_BEGIN <= now <= TIME_LOCKOUT_END):
                self.logger.log("time lockout out of bounds, ignoring digit")
                return
        self.iface.beep_buzzer()
        _i = len(self.current_input)
        self.stdout.overwrite_text = ("*" * len(self.current_input)) + digit
        self.current_input.append(digit)
        self.digit_timeout.restart()
        if len(self.password) == len(self.current_input):
            for i in range(len(self.password)):
                if self.password[i] != self.current_input[i]:
                    self.password_entered(False)
                    return
            self.password_entered(True)
        elif IMMEDIATE_REJECT:
            if self.password[_i] != self.current_input[_i]:
                self.password_entered(False)

    def digit_timeout_elapsed(self):
        """
        Handles the elapsed event of the digit timeout.
        """
        self.password_entered(False, False)
        self.stdout.overwrite_text = ""

    def cleanup(self):
        """
        Cleans up the class.
        """
        self.digit_timeout.cleanup()
        self.locked_timeout.cleanup()
        self.access_log_append("shutdown", None)
        self.access_log.close()
