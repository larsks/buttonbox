import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import logging

LCD_BLUE = P2_4 #GPIO 58
LCD_GREEN = P2_6 #GPIO 57
LCD_RED = P2_8 #GPIO 60

LOG = logging.getLogger(__name__)


class Backlight (object):
    '''A class for controlling the LEDs on a ST7565 display with
    RGB backlight.'''

    def __init__(self,
                 pin_red=LCD_RED,
                 pin_green=LCD_GREEN,
                 pin_blue=LCD_BLUE):
        self.pin_red = pin_red
        self.pin_blue = pin_blue
        self.pin_green = pin_green

        self.init_gpio()
        self.init_pwm()
        self.all_leds_off()

    def init_gpio(self):
        '''Initialize GPIO configuration.'''
        LOG.debug('initializting GPIO configuration')
        GPIO.setmode(GPIO.BCM)
        for pin in [self.pin_red, self.pin_green, self.pin_blue]:
            GPIO.setup(pin, GPIO.OUT, initial=0)

    def init_pwm(self):
        '''Initialize PWM configuration.  We are using Adafruit_BBIO.PWM to
        implement software PWM via DMA, using the PCM implementation.  We
        initalize three DMA channels, one for each color.'''
        LOG.debug('initializting PWM configuration')
        #for ch in [0, 1, 2]:
            

    def all_leds_off(self):
        '''Turn off all LEDs.'''
        self.backlight(0, 0, 0)

    def all_leds_on(self):
        '''Turn on all LEDs.'''
        self.backlight(1, 1, 1)

    def _set_led(self, pin, pwm, val):
        LOG.debug('set LED on pin %d to %s', pin, val)
        if val == 0 or val == 1:
            PWM.clear_channel(pwm)
            GPIO.output(pin, 1-int(val))
        else:
            PWM.add_channel_pulse(pwm, pin, 0, 1999 - int(1999 * val))

    @property
    def red(self):
        return self._red

    @red.setter
    def red(self, val):
        self._red = val
        self._set_led(self.pin_red,
                      0,
                      val)

    @property
    def green(self):
        return self._green

    @green.setter
    def green(self, val):
        self._green = val
        self._set_led(self.pin_green,
                      1,
                      val)

    @property
    def blue(self):
        return self._blue

    @blue.setter
    def blue(self, val):
        self._blue = val
        self._set_led(self.pin_blue,
                      2,
                      val)

    def backlight(self, red, green, blue):
        '''Set value for all three LEDs.'''
        self.red = red
        self.green = green
        self.blue = blue
