from time import sleep
from PIL import Image, ImageDraw, ImageFont
import argparse
import os
import IT8951
import logging
import asyncio
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
    p.add_argument('-u', '--url', required=True)
    p.add_argument('-w', '--width', type=int, required=True)
    p.add_argument('-t', '--height', type=int, required=True)
    p.add_argument('-o', '--output', default="screenshot.png")
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

def init_display(virtual):
    if not args.virtual:
        from IT8951.display import AutoEPDDisplay

        logging.info('Initializing EPD...')

        # here, spi_hz controls the rate of data transfer to the device, so a higher
        # value means faster display refreshes. the documentation for the IT8951 device
        # says the max is 24 MHz (24000000), but my device seems to still work as high as
        # 80 MHz (80000000)
        display = AutoEPDDisplay(vcom=-2.15, rotate=args.rotate, mirror=args.mirror, spi_hz=24000000)

        logging.info('VCOM set to {}'.format(str(display.epd.get_vcom())))

        print_system_info(display)

    else:
        from IT8951.display import VirtualEPDDisplay
        display = VirtualEPDDisplay(dims=(1872, 1404), rotate=args.rotate, mirror=args.mirror)
    return display
    

def main():
    args = parse_args()
    # screencap_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), args.output)
    screenshot = asyncio.get_event_loop().run_until_complete(capture_page.capture(args.url, args.width, args.height))
    display = init_display(args.virtual)

    try:
        display = init_display(args.virtual)
        display_image(display, screenshot)
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


if __name__ == '__main__':
    main()

