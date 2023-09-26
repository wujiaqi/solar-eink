from time import sleep
from PIL import Image, ImageOps
import argparse
import os
import io
import IT8951
import logging
import asyncio
import requests
import capture_page
from IT8951 import constants

logging.basicConfig(level=logging.INFO)


def parse_args():
    p = argparse.ArgumentParser(description='Test EPD functionality')
    p.add_argument('-v', '--virtual', action='store_true',
                   help='display using a Tkinter window instead of the '
                        'actual e-paper device (for testing without a '
                        'physical device)')
    p.add_argument('-r', '--rotate', default=None, choices=['CW', 'CCW', 'flip'],
                   help='run the tests with the display rotated by the specified value')
    p.add_argument('-m', '--mirror', action='store_true',
                   help='Mirror the display (use this if text appears backwards)')
    p.add_argument('-w', '--width', type=int, required=True)
    p.add_argument('-t', '--height', type=int, required=True)

    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help="captures a screenshot of the web page at a url and displays it on screen")
    group.add_argument('--imgurl', help="downloads image file at url and displays it on screen")
    group.add_argument('--filename', help="displays image file on screen at provided path")
    return p.parse_args()


def display_image_8bpp(display, img_path):
    logging.info('Displaying "{}"...'.format(img_path))

    # clearing image to white
    display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))

    img = Image.open(img_path)

    # TODO: this should be built-in
    dims = (display.width, display.height)

    img.thumbnail(dims)
    paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
    display.frame_buf.paste(img, paste_coords)

    display.draw_full(constants.DisplayModes.GC16)


def display_image(display, img):
    logging.info('Displaying image...')

    # clearing image to white
    display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))
    # TODO: this should be built-in
    dims = (display.width, display.height)

    img.thumbnail(dims)
    paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
    display.frame_buf.paste(img, paste_coords)

    display.draw_full(constants.DisplayModes.GC16)


def print_system_info(display):
    epd = display.epd

    logging.info('System info:')
    logging.info('  display size: {}x{}'.format(epd.width, epd.height))
    logging.info('  img buffer address: {:X}'.format(epd.img_buf_address))
    logging.info('  firmware version: {}'.format(epd.firmware_version))
    logging.info('  LUT version: {}'.format(epd.lut_version))

def init_display(virtual, rotate, mirror):
    if not virtual:
        from IT8951.display import AutoEPDDisplay

        logging.info('Initializing EPD...')

        # here, spi_hz controls the rate of data transfer to the device, so a higher
        # value means faster display refreshes. the documentation for the IT8951 device
        # says the max is 24 MHz (24000000), but my device seems to still work as high as
        # 80 MHz (80000000)
        display = AutoEPDDisplay(vcom=-2.15, rotate=rotate, mirror=mirror, spi_hz=24000000)

        logging.info('VCOM set to {}'.format(str(display.epd.get_vcom())))

        print_system_info(display)

    else:
        from IT8951.display import VirtualEPDDisplay
        display = VirtualEPDDisplay(dims=(1872, 1404), rotate=args.rotate, mirror=args.mirror)
    return display
    

def _fetch_image_from_page(url, width, height):
    return asyncio.get_event_loop().run_until_complete(capture_page.capture(url, width, height))

def _fetch_image_from_urlfile(url, resizeWidth, resizeHeight, fill, scale):
    logging.info("Downloading image from {}".format(url))
    response = requests.get(url)
    response.raise_for_status()
    logging.info("Success")
    with Image.open(io.BytesIO(response.content)) as image:
        image_ratio = image.width / image.height
        desired_ratio = resizeWidth / resizeHeight
        if fill:
            if image_ratio < desired_ratio:
                scale_factor = resizeWidth / image.width
            else:
                scale_factor = resizeHeight / image.height
            scaled_image = ImageOps.scale(image, scale_factor, resample=Image.Resampling.LANCZOS)
            return scaled_image.crop((0, 0, resizeWidth, resizeHeight))
        else:
            if image_ratio < desired_ratio:
                pad_width = resizeWidth
                pad_height = int(resizeHeight * scale)
            else:
                pad_width = int(resizeWidth * scale)
                if pad_width > resizeWidth:
                    pad_width = resizeWidth
                pad_height = resizeHeight
            padded_image = ImageOps.pad(image, (pad_width, pad_height), color=(255,255,255), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            return padded_image.crop((0, 0, resizeWidth, resizeHeight))

def do_webpage_display(url, width, height, virtual, rotate, mirror, fill):
    with _fetch_image_from_page(url, width, height, fill) as screenshot:
        _do_display(screenshot, virtual, rotate, mirror)

def do_imgurl_display(imgurl, width, height, virtual, rotate, mirror, fill, scale):
    with _fetch_image_from_urlfile(imgurl, width, height, fill, scale) as screenshot:
        _do_display(screenshot, virtual, rotate, mirror)

def do_file_display(path, width, height, virtual, rotate, mirror, fill, scale):
    with Image.open(path, 'r') as image:
        _do_display(image, virtual, rotate, mirror)
        

def _do_display(image, virtual, rotate, mirror):
    try:
        display = init_display(virtual, rotate, mirror)
        display_image(display, image)
        logging.info('Done!')
        display.epd.standby()
        logging.info('Standby...')

    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        display.epd.standby()
        exit()

    except Exception as e:
        logging.info(e)
        display.epd.standby()
        exit()

def main():
    args = parse_args()
    if args.url:
        do_webpage_display(args.url, args.width, args.height, args.virtual, args.mirror, False)
    elif args.imgurl:
        do_imgurl_display(args.imgurl, args.width, args.height, args.virtual, args.mirror, True, 1.0)
    elif args.filename:
        do_file_display(args.filename, args.width, args.height, args.virtual, args.mirror, True, 1.0)


if __name__ == '__main__':
    main()

