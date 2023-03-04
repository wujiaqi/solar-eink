#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from datetime import datetime
import time
#picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
picdir = "/mnt/nfs/eink"
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)
font18 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 18)

def get_timestamp_str():
    ts = time.time()
    date_time = datetime.fromtimestamp(ts)
    str_datetime = date_time.strftime("%B %d, %Y, %H:%M")
    return str_datetime

#screencap_path = os.path.join(picdir, 'screen_capture.png')
screencap_path = os.path.join('screenshot.png')
if os.path.exists(screencap_path) == False:
    logging.error(f"{screencap_path} not found, is nfs share mounted?")
    exit()

try:
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2.EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    logging.info("Display screen_capture.png")
    Himage = Image.open(screencap_path)
    draw = ImageDraw.Draw(Himage)
    timestamp_text = get_timestamp_str()
    draw.text((2, 0), timestamp_text, font = font18, fill = 0)
    epd.display(epd.getbuffer(Himage))
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


