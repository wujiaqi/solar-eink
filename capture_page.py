import asyncio
import argparse
import os

from pyppeteer import launch

async def capture(url, width, height, path):
    browser = await launch(options={
        'headless': True
    })
    page = await browser.newPage()
    await page.setViewport(viewport={
        'width': width,
        'height': height,
    })
    await page.goto(url, options={
        'waitUntil': 'networkidle0',
    })
    await page.screenshot({'path': path})
    await browser.close()

def main():
    parser = argparse.ArgumentParser(description='Browser screencapture utility')
    parser.add_argument('-u', '--url', required=True)
    parser.add_argument('-w', '--width', type=int, required=True)
    parser.add_argument('-t', '--height', type=int, required=True)
    args = parser.parse_args()
    # print(args.accumulate(args.integers))
    screencap_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screenshot.png')
    print('capturing to path {}'.format(screencap_path))
    asyncio.get_event_loop().run_until_complete(capture(args.url, args.width, args.height, screencap_path))
    print('Done')

if __name__ == '__main__':
    main()


