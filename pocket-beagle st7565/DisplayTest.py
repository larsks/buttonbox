import time
import random
from PIL import Image
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.SPI as SPI

import st7565.images.images as images
import st7565.fonts.fonts as fonts
import st7565.bitmap
import st7565.fonts.font5x7 as font5x7
import st7565.lcd
import st7565.ops
import st7565.spidev

lcd = st7565.lcd.LCD(adafruit=True)
lcd.clear()
screen = st7565.bitmap.Bitmap()
segoe = fonts.create_font("segoe_ui")
fonts.display_s(43,segoe, screen, lcd, 5, 10, 15)
weather_icons = images.create_images()
weather = random.choice(list(weather_icons.values()))
images.display_img(weather, screen, lcd, 50, 64)
