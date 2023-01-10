from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image

import io
import time
import logging

DASHBOARD_URL = 'http://jiaqi-desktop.local:3000/d/sPcihT2Vk/solar-e-ink?orgId=1&kiosk'
SCREENSHOT_PATH = "screen_capture.png"

def render_image():
    chrome_options = Options()
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
    chrome_options.add_argument("--window-size=800,480")
    chrome_options.add_argument("--kiosk")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--force-device-scale-factor=1')
    driver = webdriver.Chrome(options=chrome_options)
    logging.info("Initializing Chrome Web Driver")
    logging.info("Loading URL {url}".format(url=DASHBOARD_URL))
    driver.get(DASHBOARD_URL)
    time.sleep(3.0)
    logging.info("Loaded. Saving screenshot...")
    # capture_bytes = driver.get_screenshot_as_png()
    driver.save_screenshot(SCREENSHOT_PATH)
    logging.info("saved screenshot as {path}".format(path=SCREENSHOT_PATH))
    driver.close()
    # return capture_bytes

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s-%(levelname)s-%(message)s")
    capture_bytes = render_image()
    # im = Image.open(io.BytesIO(capture_bytes))
    # im.show()
    logging.info("done")
    

if __name__ == "__main__":
    main()
