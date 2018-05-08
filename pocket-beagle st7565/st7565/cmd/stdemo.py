#!/usr/bin/python

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.SPI as SPI
#GPIO.setwarnings(False)

import time
import argparse
import threading
import math

from pkg_resources import Requirement, resource_filename

from itertools import cycle
from PIL import Image

#import st7565.backlight
import st7565.lcd
import st7565.bitmap

args = None
leds = None
lcd = None
screen = None


def pulse():
    for angle in cycle(range(0, 361)):
        r = (math.sin(math.radians(angle)) + 1)/2
        g = (math.sin(math.radians((angle + 90) % 360)) + 1)/2
        b = (math.sin(math.radians((angle + 180) % 360)) + 1)/2

        #leds.backlight(r, g, b)
        time.sleep(0.01)


def parse_args():
    p = argparse.ArgumentParser()

    g = p.add_argument_group('GPIO')
    g.add_argument('--pin-a0', type=int)
    g.add_argument('--pin-rst', type=int)
    g.add_argument('--pin-red', type=int)
    g.add_argument('--pin-green', type=int)
    g.add_argument('--pin-blue', type=int)

    g = p.add_argument_group('SPI')
    g.add_argument('--spi-bus', default=0)
    g.add_argument('--spi-dev', default=0)

    g = p.add_argument_group('Animation')
    g.add_argument('--spin',
                   action='store_const',
                   const='spin',
                   dest='animation')
    g.add_argument('--hscroll',
                   action='store_const',
                   const='hscroll',
                   dest='animation')
    g.add_argument('--vscroll',
                   action='store_const',
                   const='vscroll',
                   dest='animation')

    g.add_argument('--step', type=int)
    g.add_argument('--delay', default=0.001, type=float)
    g.add_argument('--pulse', action='store_true')
    g.add_argument('--wild', action='store_true')

    p.add_argument('--no-init', action='store_true')
    p.add_argument('--adafruit', '-a',
                   action='store_true', default=False)
    p.add_argument('image',
                   nargs='?',
                   default=resource_filename(
                       'st7565', 'images/tux.pbm'))

    return p.parse_args()


def display_image(img):
    '''Display an image on the LCD screen.'''
    screen.drawbitmap(img, centerx=True, centery=True)
    lcd.write_buffer(screen)


def vscroll_image(img):
    '''Display an image on the LCD screen and scroll it vertically.'''
    screen.drawbitmap(img, centerx=True, centery=True)

    while True:
        screen.vscroll(args.step)
        lcd.write_buffer(screen)
        time.sleep(args.delay)


def hscroll_image(img):
    '''Display an image on the LCD screen and scroll it horizontally.'''
    screen.drawbitmap(img, centerx=True, centery=True)

    while True:
        screen.hscroll(args.step)
        lcd.write_buffer(screen)
        time.sleep(args.delay)


def spin_image(img):
    '''Display an image on the LCD screen and spin it.'''
    lcd.pos(4, 24)
    lcd.puts('Generating frames...')

    work = img.convert('RGBA')

    frames = []
    for angle in range(0, 360, args.step):
        lcd.pos(4)
        lcd.puts('%3s' % (int((angle/360.0) * 100)))
        lcd.send_data([0xff] * int(angle/360.0 * (128-24)))

        x = work.rotate(angle, expand=True)
        x = x.crop(box=(x.size[0]/2 - work.size[0]/2,
                        x.size[1]/2 - work.size[1]/2,
                        x.size[0]/2 + work.size[0]/2,
                        x.size[1]/2 + work.size[1]/2))
        mask = Image.new('RGBA', x.size, (255,) * 4)
        out = Image.composite(x, mask, x)
        screen.drawbitmap(out.convert('1'), centerx=True, centery=True)
        frames.append(screen[:])

    while True:
        for frame in frames:
            lcd.write_buffer(frame)
            time.sleep(args.delay)


def main():
    global args, lcd, leds, screen

    args = parse_args()

    if args.wild:
        args.spin = args.pulse = True

    lcd_kwargs = {}
    #backlight_kwargs = {}
    
    if args.pin_a0 is not None:
        lcd_kwargs['pin_a0'] = args.pin_a0
    if args.pin_rst is not None:
        lcd_kwargs['pin_rst'] = args.pin_rst
    if args.spi_bus is not None:
        lcd_kwargs['spi_bus'] = args.spi_bus
    if args.spi_dev is not None:
        lcd_kwargs['spi_dev'] = args.spi_dev
    if args.no_init:
        lcd_kwargs['init'] = False
    """
    if args.pin_red is not None:
        backlight_kwargs['pin_red'] = args.pin_red
    if args.pin_green is not None:
        backlight_kwargs['pin_green'] = args.pin_green
    if args.pin_blue is not None:
        backlight_kwargs['pin_blue'] = args.pin_blue
    """    
        
    lcd = st7565.lcd.LCD(adafruit=args.adafruit, **lcd_kwargs)
    #leds = st7565.backlight.Backlight(**backlight_kwargs)
    screen = st7565.bitmap.Bitmap()

    img = Image.open(args.image)

    lcd.clear()
    #leds.all_leds_on()

    if args.pulse:
        t = threading.Thread(target=pulse)
        t.start()

    if args.animation == 'spin':
        args.step = 10 if args.step is None else args.step
        spin_image(img)
    elif args.animation == 'hscroll':
        args.step = 1 if args.step is None else args.step
        hscroll_image(img)
    elif args.animation == 'vscroll':
        args.step = 1 if args.step is None else args.step
        vscroll_image(img)
    #display_image(img)
    
    lcd_test = st7565.lcd.LCD(adafruit=True)
    lcd_test.display_points_normal()
    screen_test = st7565.bitmap.Bitmap()
    time.sleep(3)
    screen_test.box(5, 5, 10, 10)
    lcd_test.write_buffer(screen_test)
    


if __name__ == '__main__':
    main()
