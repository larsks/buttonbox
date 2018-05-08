#!/usr/bin/python

import time
import argparse
import logging

import st7565.backlight


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--pins',
                   nargs=3)
    p.add_argument('--frequency')
    p.add_argument('--on',
                   action='store_true',
                   dest='all_leds')
    p.add_argument('--off',
                   action='store_false',
                   dest='all_leds')

    p.add_argument('--rgb', '-r',
                   nargs=3)

    p.add_argument('--debug',
                   action='store_const',
                   const='DEBUG',
                   dest='loglevel')

    p.add_argument('--wait',
                   action='store_true',
                   help=argparse.SUPPRESS)

    p.set_defaults(loglevel='WARN', all_leds=None)

    return p.parse_args()


def main():
    global leds
    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    kwargs = {}
    if args.pins:
        kwargs['pin_red'] = args.pins[0]
        kwargs['pin_green'] = args.pins[1]
        kwargs['pin_blue'] = args.pins[2]

    if args.frequency:
        kwargs['freq'] = args.frequency

    leds = st7565.backlight.Backlight(**kwargs)

    if args.all_leds is True:
        leds.all_leds_on()
    elif args.all_leds is False:
        leds.all_leds_off()
    elif args.rgb:
        for i, attr in enumerate(('red', 'green', 'blue')):
            if args.rgb[i] != '-':
                val = float(args.rgb[i])
                setattr(leds, attr, val)
                if val > 0 and val < 1:
                    args.wait = True

    if args.wait:
        while True:
            time.sleep(300)

if __name__ == '__main__':
    main()
