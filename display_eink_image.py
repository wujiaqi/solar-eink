#!/usr/bin/python
# -*- coding:utf-8 -*-
import argparse
import asyncio
import logging
import os
import sys
import time
import traceback
from datetime import datetime

import capture_page
from PIL import Image, ImageDraw, ImageFont
import epaper

fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

def parse_args():
    p = argparse.ArgumentParser(description='EPD image displayer, for waveshare_epd python library supported displays')
    p.add_argument('-u', '--url', required=True)
    p.add_argument('-e', '--epd', help='epd modeule name', required=True)
    return p.parse_args()

def get_timestamp_str():
    ts = time.time()
    date_time = datetime.fromtimestamp(ts)
    str_datetime = date_time.strftime("%B %d, %Y, %H:%M")
    return str_datetime


def main():
    font18 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 18)
    args = parse_args()
    epd = epaper.epaper('epd7in5_V2').EPD()
    screenshot = asyncio.get_event_loop().run_until_complete(capture_page.capture(args.url, epd.width, epd.height))

    try:        
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        logging.info(f"Displaying image...")
        draw = ImageDraw.Draw(screenshot)
        timestamp_text = get_timestamp_str()
        draw.text((2, 0), timestamp_text, font = font18, fill = 0)
        epd.display(epd.getbuffer(screenshot))
        time.sleep(2)

        logging.info("Goto Sleep...")
        epd.sleep()
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd.epdconfig.module_exit()
        exit()

    except Exception as e:
        logging.info(e)
        epd.epdconfig.module_exit()
        exit()


if __name__ == '__main__':
    main()

