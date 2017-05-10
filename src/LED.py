import RPi.GPIO as GPIO
LED_GPIO = [
    5,
    6,
    12,
    13,
    16,
    19,
    20,
    26
]

def setup_leds():
    GPIO.setmode(GPIO.BCM)
    for l in LED_GPIO:
        GPIO.setup(l, GPIO.OUT)


def set_leds(percent):
    """
    :param: percent: a number from 0-1 that represents the current percentage along that the timeout is
    """
    on_LED = int(percent/12) #Number of LED that must be on
    nmb_LED = len(LED_GPIO)
    
    for i in range(nmb_LED):
        if on_LED > 0:
            GPIO.output(LED_GPIO[i], True)
            nmb_LED = nmb_LED - 1
        else:
            GPIO.output(LED_GPIO[i], False)
