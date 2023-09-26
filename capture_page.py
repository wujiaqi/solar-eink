import argparse
import asyncio
import io
import os
import platform
import sys

from PIL import Image
from pyppeteer import launch


def get_chromium_path():
    if sys.platform.startswith('linux') and (platform.uname().machine.startswith('aarch') or platform.uname().machine.startswith('armv')):
        return '/usr/bin/chromium-browser'
    elif sys.platform.startswith('darwin'):
        return '/opt/homebrew/bin/chromium'

async def capture(url, width, height):
    browser_opts = {
        'headless': True,
    }
    browser_opts['executablePath'] = get_chromium_path()
    browser = await launch(options=browser_opts)
    page = await browser.newPage()
    await page.setViewport(viewport={
        'width': width,
        'height': height,
    })
    await page.goto(url, options={
        'waitUntil': 'networkidle0',
        'timeout': 60000
    })
    # await page.screenshot({'path': path})
    screenshot = await page.screenshot({'encoding': 'binary'})
    image = Image.open(io.BytesIO(screenshot))
    await browser.close()
    return image

def parse_args():
    parser = argparse.ArgumentParser(description='Browser screencapture utility')
    parser.add_argument('-u', '--url', required=True)
    parser.add_argument('-w', '--width', type=int, required=True)
    parser.add_argument('-t', '--height', type=int, required=True)
    return parser.parse_args()

def main():
    args = parse_args()
    output = asyncio.get_event_loop().run_until_complete(capture(args.url, args.width, args.height))
    print('Done')
    screencap_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screenshot.png')
    print('capturing to path {}'.format(screencap_path))
    output.save(screencap_path)

if __name__ == '__main__':
    main()


