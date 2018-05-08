import ctypes
import logging

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.SPI as SPI

import st7565.spidev
import st7565.ops
import st7565.fonts.font5x7 as font5x7

LOG = logging.getLogger(__name__)

libc = ctypes.CDLL('libc.so.6')

BRIGHTNESS = 0x20

LCD_RST = "P2_20" #GPIO 64 being used as digital reset
LCD_A0 = "P2_19" #GPIO 27
SPI_BUS = 2
SPI_DEV = 1

BIAS_1_9 = 0
BIAS_1_7 = 1

STATIC_OFF = 0
STATIC_ON_LONG = 1
STATIC_ON_SHORT = 2
STATIC_ALWAYS_ON = 3

RESISTOR_RATIO = {
    3.0: 0b000,
    3.5: 0b001,
    4.0: 0b010,
    4.5: 0b011,
    5.0: 0b100,
    5.5: 0b101,
    6.0: 0b110,
    6.4: 0b111,
}


def delayus(us):
    '''Delay microseconds with libc usleep() using ctypes.'''
    libc.usleep(int(us))


def delayms(ms):
    '''Delay microseconds with libc usleep() using ctypes.'''
    libc.usleep(int(ms) * 1000)


class LCD (object):

    def __init__(self,
                 pin_rst=LCD_RST,
                 pin_a0=LCD_A0,
                 spi_bus=SPI_BUS,
                 spi_dev=SPI_DEV,
                 brightness=BRIGHTNESS,
                 init=True,
                 adafruit=False):

        self.pin_rst = pin_rst
        self.pin_a0 = pin_a0
        self.spi_bus = spi_bus
        self.spi_dev = spi_dev
        self.brightness = brightness
        self.adafruit = adafruit

        if adafruit:
            self.pagemap = [3, 2, 1, 0, 7, 6, 5, 4]
        else:
            self.pagemap = None

        self.init_spi()
        self.init_gpio()

        if init:
            self.init_lcd()
    
    def init_gpio(self):
        '''Initialize GPIO configuration. 
        Configure RST and A0 outputs.'''
        for pin in [LCD_RST, LCD_A0]:
            GPIO.setup(pin, GPIO.OUT, initial = 1)
    
    def init_spi(self):
        '''Open connection to kernel SPI device.'''
        self.spi = st7565.spidev.SpiDev(self.spi_bus, self.spi_dev)

    def init_lcd(self):
        '''Initialize the LCD.  Based on code from
        <https://github.com/adafruit/ST7565-LCD/blob/master/c/stlcd.c>'''

        self.reset()
        self.soft_reset()
        self.bias_set(bias=BIAS_1_7)
        self.adc_select()
        self.common_output_mode_select()
        self.display_start_line_set()

        LOG.debug('power on')
        self.power_control_set(True, False, False)
        delayms(50)
        self.power_control_set(True, True, False)
        delayms(50)
        self.power_control_set(True, True, True)
        delayms(10)

        self.regulator_resistor_select(ratio=6.0)
        self.brightness_set(self.brightness)

        LOG.debug('display on')
        self.display_on()
        self.display_points_normal()

        LOG.debug('clear')
        self.clear()

    def clear(self):
        '''Clear the display. Writes 0x00 to all display positions.'''
        for page in range(8):
            LOG.debug('clear page %d', page)
            self.page_set(page)
            self.column_set(0)
            self.send_data([0x00] * 128)

        self.page_set(0)
        self.column_set(0)

    def page_set(self, page):
        '''Set the current page.'''
        if self.pagemap:
            page = self.pagemap[page]

        op = st7565.ops.PAGE_SET | page
        self.send_command([op])

    def column_set(self, col):
        '''Set the current column.'''
        if self.adafruit:
            col += 1

        # set column lsb
        lsb = (col & 0x0f)
        self.send_command([st7565.ops.COLUMN_SET_LSB | lsb])

        # set column msb
        msb = (col & 0xf0) >> 4
        self.send_command([st7565.ops.COLUMN_SET_MSB | msb])

    def pos(self, page, col=0):
        '''Set the current page and column.  If unspecified, col defaults
        to 0.'''
        self.page_set(page)
        self.column_set(col)

    def _set_pin(self, pin):
        GPIO.output(pin, 1)

    def _reset_pin(self, pin):
        GPIO.output(pin, 0)

    def reset(self):
        '''Perform a hard reset of the LCD by bring the RST line low for
        500 ms'''
        LOG.debug('hard reset')
        self._reset_pin(self.pin_rst)
        delayms(500)
        self._set_pin(self.pin_rst)
        delayms(1)

    def send_command(self, bytes):
        '''Send a command to the LCD.  Brings A0 low then sends the data
        via SPI.'''
        LOG.debug('sending command: %s',
                  ' '.join(hex(x) for x in bytes))
        self._reset_pin(self.pin_a0)
        self.send(bytes)

    def send_data(self, bytes):
        '''Send a command to the LCD.  Brings A0 high then sends the data
        via SPI.'''
        LOG.debug('sending data: %s',
                  ' '.join(hex(x) for x in bytes))
        self._set_pin(self.pin_a0)
        self.send(bytes)

    def send(self, bytes):
        '''Send bytes to the LCD via SPI protocol.'''
        self.spi.write(bytes)

    def soft_reset(self):
        self.send_command([st7565.ops.RESET])

    def display_on(self):
        self.send_command([st7565.ops.DISPLAY_ON])

    def display_off(self):
        self.send_command([st7565.ops.DISPLAY_OFF])

    def display_points_on(self):
        '''Turn all pixels on.'''
        self.send_command([st7565.ops.DISPLAY_ALL_POINTS_ON])

    def display_points_normal(self):
        '''Revert to normal display after `display_points_on`.'''
        self.send_command([st7565.ops.DISPLAY_ALL_POINTS_NORMAL])

    def display_reverse(self):
        '''Reverse the display.'''
        self.send_command([st7565.ops.DISPLAY_REVERSE])

    def display_normal(self):
        '''Return to normal display after `display_reverse`.'''
        self.send_command([st7565.ops.DISPLAY_NORMAL])

    def adc_select(self, reverse=False):
        op = st7565.ops.ADC_SELECT | int(reverse)
        self.send_command([op])

    def common_output_mode_select(self, reverse=False):
        op = st7565.ops.COMMON_OUTPUT_MODE_SELECT | (int(reverse) << 3)
        self.send_command([op])

    def bias_set(self, bias=BIAS_1_9):
        if bias not in [BIAS_1_9, BIAS_1_7]:
            raise ValueError(bias)

        op = st7565.ops.BIAS_SET | (int(bias))
        self.send_command([op])

    def power_control_set(self,
                          converter=False,
                          regulator=False,
                          follower=False):

        op = (st7565.ops.POWER_CONTROL_SET
              | (int(converter) << 2)
              | (int(regulator) << 1)
              | (int(follower)))

        self.send_command([op])

    def regulator_resistor_select(self, ratio=5.0):
        if ratio not in RESISTOR_RATIO:
            raise ValueError(ratio)

        op = st7565.ops.REGULATOR_RESISTOR_SET | RESISTOR_RATIO[ratio]
        self.send_command([op])

    def display_start_line_set(self, line=0):
        if line > 64:
            raise ValueError(line)

        op = st7565.ops.DISPLAY_START_LINE_SET | line
        self.send_command([op])

    def brightness_set(self, val):
        '''Set the display brightness.'''
        self.send_command([st7565.ops.BRIGHTNESS_SET, val])

    def set_static_indicator(self, on=True, mode=STATIC_ALWAYS_ON):
        if mode not in range(0, 4):
            raise ValueError(mode)

        op = st7565.ops.STATIC_INDICATOR_SET | int(on)
        self.send_command([op, mode])

    def sleep(self):
        '''Put the LCD to sleep.'''
        self.set_static_indicator(False, mode=STATIC_OFF)
        self.display_off()
        self.display_points_on()

    def wake(self):
        '''Wake the LCD.'''
        self.soft_reset()
        self.brightness_set(self.brightness)
        self.display_points_normal()
        self.display_on()
        self.set_static_indicator(True)

    def putc(self, c):
        '''Draw a single character at the current position.'''
        bytes = font5x7.glyphs[ord(c) - font5x7.min_char]
        self.send_data(bytes + [0x00] * (len(bytes)-font5x7.char_width))

    def puts(self, s):
        '''Draw a string of characters at the current position.'''
        for c in s:
            self.putc(c)

    def write_buffer(self, buffer):
        '''Write an entire 8x128 buffer to the LCD.'''
        for p in range(8):
            self.page_set(p)
            self.column_set(0)
            bytes = buffer[128*p:128*p+128]
            self.send_data(bytes)


if __name__ == '__main__':
    logging.basicConfig(
        level='DEBUG')
    l = LCD(adafruit=True)
    print("TURN EVERYTHING ON")
    l.display_points_on()
