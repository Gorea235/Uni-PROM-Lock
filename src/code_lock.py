from timeout import *
import os

PWORD_FILE = "password.txt"
DEFAULT_PWORD = "1234"
IMMEDIATE_REJECT = False

class CodeLock(object):

    def __init__(self, iface, logger, password):
        self.iface = iface
        self.logger = logger
        self.iface.digit_received.bind(self.digit_received)
        self.password = []
        if os.path.isfile(PWORD_FILE):
            with open(PWORD_FILE) as f:
                self.password = f.read().strip().split()
            self.logger.log("password read as {}", self.password)
        else:
            self.password = DEFAULT_PWORD.split()
            self.logger.log("password defaulted to {}", self.password)
            with open(PWORD_FILE, "w") as f:
                f.write("".join(self.password))
            self.logger.log("wrote new password file to {}", PWORD_FILE)
        self.digit_timeout = Timeout(3)
        self.current_input = []
        self.locked_out = False
        self.incorrect_attempts = 0

    def password_entered(self):
        self.digit_timeout.reset()

    def password_correct(self):
        self.password_entered()
        self.incorrect_attempts = 0
        self.iface.flash_green_led()

    def password_incorrect(self, count_attempt=True):
        self.password_entered()
        if count_attempt:
            self.incorrect_attempts += 1
        self.iface.flash_red_led()

    def lockout(self):
        self.incorrect_attempts = 0
        self.locked_out = True

    def digit_received_handler(self, digit):
        if self.locked_out:
            return
        self.iface.beep_buzzer()
        _i = len(self.current_input)
        self.current_input.append(digit)
        self.digit_timeout.restart()
        if len(self.password) == len(self.current_input):
            for i in range(len(self.password)):
                if self.password[i] != self.current_input[i]:
                    self.password_incorrect()
                    return
            self.password_correct()
        elif IMMEDIATE_REJECT:
            if self.password[_i] != self.current_input[_i]:
                self.password_incorrect()

    def digit_timeout_elapsed(self):
        self.password_incorrect(count_try=False)

    def cleanup(self):
        self.digit_timeout.reset()
