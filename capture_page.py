import asyncio
import argparse
import os
import sys
import platform

from pyppeteer import launch

def get_chromium_path():
    if sys.platform.startswith('linux') and platform.uname().machine.startswith('armv'):
        return '/usr/bin/chromium-browser'
    elif sys.platform.startswith('darwin'):
        return '/opt/homebrew/bin/chromium'

async def capture(url, width, height, path):
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
    })
    # await page.screenshot({'path': path})
    screenshot = await page.screenshot({'encoding': 'base64'})
    await browser.close()
    return screenshot

def main():
    parser = argparse.ArgumentParser(description='Browser screencapture utility')
    parser.add_argument('-u', '--url', required=True)
    parser.add_argument('-w', '--width', type=int, required=True)
    parser.add_argument('-t', '--height', type=int, required=True)
    args = parser.parse_args()
    # print(args.accumulate(args.integers))
    screencap_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screenshot_.png')
    print('capturing to path {}'.format(screencap_path))
    output = asyncio.get_event_loop().run_until_complete(capture(args.url, args.width, args.height, screencap_path))
    print(output[0:10])
    print('Done')

if __name__ == '__main__':
    main()


