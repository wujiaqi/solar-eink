#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from datetime import datetime
import time
import asyncio
import capture_page
import argparse
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
picdir = "/mnt/nfs/eink"
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image, ImageDraw, ImageFont
import traceback


def parse_args():
    p = argparse.ArgumentParser(description='Test EPD functionality')
    p.add_argument('-u', '--url', required=True)
    p.add_argument('-w', '--width', type=int, required=True)
    p.add_argument('-t', '--height', type=int, required=True)
    return p.parse_args()

def get_timestamp_str():
    ts = time.time()
    date_time = datetime.fromtimestamp(ts)
    str_datetime = date_time.strftime("%B %d, %Y, %H:%M")
    return str_datetime


def main():
    font18 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 18)
    args = parse_args()
    screenshot = asyncio.get_event_loop().run_until_complete(capture_page.capture(args.url, args.width, args.height))

    try:
        logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        
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
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()

    except Exception as e:
        logging.info(e)
        epd7in5_V2.epdconfig.module_exit()
        exit()


if __name__ == '__main__':
    main()

