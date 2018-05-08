# Reference:
# https://www.adafruit.com/images/product-files/250/TG12864H3-04MA0_A00.pdf

PAGE_SET                       = 0b10110000  # B0
COLUMN_SET_LSB                 = 0b00000000  # 00
COLUMN_SET_MSB                 = 0b00010000  # 10
ADC_SELECT                     = 0b10100000  # A0
COMMON_OUTPUT_MODE_SELECT      = 0b11000000  # C0
BIAS_SET                       = 0b10100010  # A2
POWER_CONTROL_SET              = 0b00101000  # 28
REGULATOR_RESISTOR_SET         = 0b00100000  # 20
DISPLAY_START_LINE_SET         = 0b01000000  # 40
BRIGHTNESS_SET                 = 0b10000001  # 81
STATIC_INDICATOR_SET           = 0b10101100  # AC
DISPLAY_ON                     = 0b10101111  # AF
DISPLAY_OFF                    = 0b10101110  # AE
DISPLAY_ALL_POINTS_ON          = 0b10100101  # A5
DISPLAY_ALL_POINTS_NORMAL      = 0b10100100  # A4
DISPLAY_REVERSE                = 0b10100111  # A7
DISPLAY_NORMAL                 = 0b10100110  # A6
RMW                            = 0b11100000  # E0
BOOSTER_RATIO_SET              = 0b11111000  # F8
NOP                            = 0b11100011  # E3
RESET                          = 0b11100010  # E2

# flake8: noqa
