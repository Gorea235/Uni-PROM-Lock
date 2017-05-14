#! /usr/bin/env python3
import datetime
import time
import os
from timeout import *
import subprocess

pi_leds_available = True
_pi_leds_import_error = None
try:
    import LED as pi_leds
except ImportError as ex:
    pi_leds_available = False
    _pi_leds_import_error = ex

DIGIT_TIMEOUT_LENGTH = 3
PWORD_FILE = "password.txt"
ACCESS_LOG_FILE = "access_log.csv"
GNUPLOT_FILE = "gnuplot_data.csv"
DEFAULT_PWORD = "1234"
IMMEDIATE_REJECT = True
TIME_LOCKOUT_BEGIN = datetime.time(0, 0)  # hour, minute
TIME_LOCKOUT_END = datetime.time(0, 0)  # hour, minute
USE_MAX_ATTEMPTS = False
LOCKED_OUT_TIME = 60
MAX_ATTEMPTS = 5
PRINT_MSGS = True


class CodeLock:
    def __init__(self, iface, logger, stdout, DEMO_MODE=False):
        self.DEMO_MODE = DEMO_MODE
        self.iface = iface  # store interface wrapper
        self.logger = logger  # store logger
        self.stdout = stdout  # store standard output

        if not self.DEMO_MODE:
            self.stdout.start_overwrite_output()

        # bind to digit recevied event
        self.iface.digit_received.bind(self.digit_received_handler)
        self._digit_timeout_time = None
        self.digit_timeout = Timeout(0.1)  # the digit timeout
        self.digit_timeout.elapsed.bind(self.digit_timeout_elapsed)

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
        self.locked_timeout.elapsed.bind(self.locked_timeout_elapsed)
        self.incorrect_attempts = 0  # the number of incorrect attempts
        self.locked_time_left = 0  # the amount of time left for the user to be locked out
        self.ignore_digits = False
        self.correct_clear_timeout = Timeout(3)
        self.correct_clear_timeout.elapsed.bind(self.clear_timeout_elapsed)
        self.incorrect_clear_timeout = Timeout(1)
        self.incorrect_clear_timeout.elapsed.bind(self.clear_timeout_elapsed)
        self.cover_digit_timeout = Timeout(1)
        self.cover_digit_timeout.elapsed.bind(self.cover_digit_timeout_elapsed)

        if pi_leds_available:
            pi_leds.setup_leds()
        else:
            self.logger.logw(
                "unable to import LED lib, RPi LEDs will not be functional")
            self.logger.loge(_pi_leds_import_error)

        self.logger.log("code lock init complete")

    def access_log_append(self, event_name, success):
        self.access_log.write(
            "{},{:%Y-%m-%dT%H:%M:%S},{}\n".format(event_name, datetime.datetime.now(), success))

    def password_entered(self, correct, count_attempt=True):
        """
        Resets digit timeout and stores the time of entry. Also handles the attempts count and LEDs.
        """
        self.digit_timeout.reset()
        self.ignore_digits = True
        self.current_input = []
        if pi_leds_available:
            pi_leds.set_leds(0)
        self.access_log_append("code", correct)
        if correct:
            if PRINT_MSGS:
                print("Unlocked!")
            self.correct_clear_timeout.restart()
            self.incorrect_attempts = 0
            self.iface.flash_green_led()
            self.logger.log("password correct, attempts reset and LED pulsed")
        else:
            if count_attempt and USE_MAX_ATTEMPTS:
                self.incorrect_attempts += 1
                if PRINT_MSGS:
                    print("Incorrect, you have {} more tries left".format(
                        MAX_ATTEMPTS - self.incorrect_attempts))
            elif count_attempt and not USE_MAX_ATTEMPTS and PRINT_MSGS:
                print("Incorrect!")
            self.incorrect_clear_timeout.restart()
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
        self.stdout.overwrite_text = "LOCKED ({})".format(
            self.locked_time_left)
        if self.locked_time_left <= 0:
            self.locked_out = False
            self.overwrite_text = ""
            self.logger.log("locked timeout finished, disabling")
        else:
            self.locked_timeout.start()
            self.logger.logd("restarted timeout second counter")

    def clear_timeout_elapsed(self):
        self.cover_digit_timeout.reset()
        self.stdout.overwrite_text = ""
        self.ignore_digits = False

    def cover_digit_timeout_elapsed(self):
        self.overwrite_text = "*" * len(self.current_input)

    def digit_received_handler(self, digit):
        """
        Handles the event when the user inputs a digit into the keypad.
        """
        self.logger.log("received digit '{}'".format(digit))
        if self.ignore_digits:
            self.logger.log("currently ignoring digits, skipping")
            return
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
        self.cover_digit_timeout.restart()
        self.current_input.append(digit)
        self._digit_timeout_time = time.time()
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
        now = time.time()
        passed = now - self._digit_timeout_time
        self.logger.logd(
            "digit timeout: {} seconds have passed since last input", passed)
        if pi_leds_available:
            pi_leds.set_leds(max(0, min(passed / DIGIT_TIMEOUT_LENGTH, 1)))
        if passed >= DIGIT_TIMEOUT_LENGTH:
            self.password_entered(False, False)
            self.stdout.overwrite_text = ""
        else:
            self.digit_timeout.restart()

    def cleanup(self):
        """
        Cleans up the class.
        """
        if not self.DEMO_MODE:
            self.stdout.end_overwrite_output()
        self.digit_timeout.cleanup()
        self.locked_timeout.cleanup()
        self.correct_clear_timeout.cleanup()
        self.incorrect_clear_timeout.cleanup()
        self.cover_digit_timeout.cleanup()
        self.access_log_append("shutdown", None)
        self.access_log.close()
        data = []
        try:
            with open(ACCESS_LOG_FILE) as f:
                for l in f:
                    spl = l.strip().split(",")
                    if spl[0] == "startup":
                        data.clear()
                    elif spl[0] == "code":
                        ts = spl[1].split("T")[1].split(":")
                        s = (int(ts[0]) * 3600) + \
                            (int(ts[1]) * 60) + int(ts[2])
                        data.append("{}\t{}".format(s, int(eval(spl[2]))))
            with open(GNUPLOT_FILE, "w") as f:
                f.write("\n".join(data))
            try:
                subprocess.call(["./gnuplot.sh"])
            except Exception as ex:
                if PRINT_MSGS:
                    import traceback
                    traceback.print_exc()
# self.logger.loge(
# ex, "An error occured while attempting to run GnuPlot")
        except Exception as ex:
            if PRINT_MSGS:
                import traceback
                traceback.print_exc()
