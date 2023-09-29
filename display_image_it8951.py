from time import sleep
from PIL import Image, ImageOps
import argparse
import numpy as np
import os
import io
import traceback
import IT8951
import logging
import asyncio
import requests
import capture_page
import threading
import multiprocessing
import math
from numba import jit
from tqdm import tqdm
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

    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help="captures a screenshot of the web page at a url and displays it on screen")
    group.add_argument('--imgurl', help="downloads image file at url and displays it on screen")
    group.add_argument('--filename', help="displays image file on screen at provided path")
    return p.parse_args()

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
        display = AutoEPDDisplay(vcom=-1.37, rotate=rotate, mirror=mirror, spi_hz=24000000)

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
        logging.info("scaling image to {} x {}".format(resizeWidth, resizeHeight))
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

def do_webpage_display(display, url, dither_levels=0):
    with _fetch_image_from_page(url, display.width, display.height) as screenshot:
        _do_display(display, screenshot, dither_levels=dither_levels)

def do_imgurl_display(display, imgurl, fill, scale, dither_levels=0):
    with _fetch_image_from_urlfile(imgurl, display.width, display.height, fill, scale) as screenshot:
        _do_display(display, screenshot, dither_levels=dither_levels)

def do_file_display(display, path, dither_levels=0):
    with Image.open(path, 'r') as image:
        padded_image = ImageOps.pad(image, (display.width, display.height), color=(255,255,255), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        _do_display(display, padded_image, dither_levels=dither_levels)
        

# From https://scipython.com/blog/floyd-steinberg-dithering/
@jit(nopython=True)
def get_new_val(old_val, nc):
    """
    Get the "closest" colour to old_val in the range [0,1] per channel divided
    into nc values.

    """
    if old_val == 1.0 or old_val == 0.0:
        return old_val

    return round(old_val * (nc - 1)) / (nc - 1)


def fs_dither(img, nc):
    """
    Floyd-Steinberg dither the image img into a palette with nc colours per
    channel.

    """

    arr = np.array(img, dtype=float) / 255
    arr_dithered = floyd_steinberg(arr, nc)

    carr = np.array(arr_dithered/np.max(arr_dithered, axis=(0,1)) * 255, dtype=np.uint8)
    return Image.fromarray(carr)

@jit(nopython=True)
def floyd_steinberg(arr, nc):
    h, w = arr.shape
    for ir in range(h):
        for ic in range(w):
            # NB need to copy here for RGB arrays otherwise err will be (0,0,0)!
            old_val = arr[ir, ic]
            new_val = get_new_val(old_val, nc)
            arr[ir, ic] = new_val
            err = old_val - new_val
            # In this simple example, we will just ignore the border pixels.
            if ic < w - 1:
                arr[ir, ic+1] += err * 0.4375 # right, 7/16
            if ir < h - 1:
                if ic > 0:
                    arr[ir+1, ic-1] += err * 0.1875 # left, down, 3/16
                arr[ir+1, ic] += err * 0.3125 # down, 5/16
                if ic < w - 1:
                    arr[ir+1, ic+1] += err * 0.1875 # right, down, 1/16
    return arr

def _get_thread_img_box(image, threads, thread_number):
    return (0, int(image.height / threads * thread_number), image.width, image.height if thread_number == threads else int(image.height / threads * (thread_number + 1)))

def _dither_threaded(image, nc, num_threads):
    threads = []
    for i in range(num_threads):
        cropped_image = image.crop(_get_thread_img_box(image, num_threads, i))
        threads.append(threading.Thread(target=_dither_worker, args=(cropped_image, nc, image, num_threads, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return image


def _dither_worker(crop_image, nc, result, threads, thread_index):
    with fs_dither(crop_image, nc) as dithered_image:
        result.paste(dithered_image, box=_get_thread_img_box(result, threads, thread_index))

def _do_display(display, image, dither_levels=0):
    try:
        with image.convert('L') as image_gs:
            processed_image = image
            if dither_levels > 0:
                processed_image = _dither_threaded(image_gs, dither_levels, multiprocessing.cpu_count()) # floyd steinberg dithering is too slow on raspberry pi even with multithreading
            dims = (display.width, display.height)
            paste_coords = [dims[i] - processed_image.size[i] for i in (0,1)]  # align image with bottom of display
            display.frame_buf.paste(processed_image, paste_coords)
            display.draw_full(constants.DisplayModes.GC16)
        logging.info('Done!')
        display.epd.sleep()
        logging.info('Putting display to sleep...')

    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        logging.info('Putting display to sleep...')
        display.epd.sleep()
        exit()

    except Exception as e:
        logging.info(e)
        traceback.print_exc()
        logging.info('Putting display to sleep...')
        display.epd.sleep()
        exit()

def main():
    args = parse_args()
    display = init_display(args.virtual, args.rotate, args.mirror)
    if args.url:
        do_webpage_display(display, args.url)
    elif args.imgurl:
        do_imgurl_display(display, args.imgurl, True, 1.0)
    elif args.filename:
        do_file_display(display, args.filename)


if __name__ == '__main__':
    main()

