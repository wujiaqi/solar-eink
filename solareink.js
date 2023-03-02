const puppeteer = require('puppeteer');

(async () => {
  // Create a browser instance
  const browser = await puppeteer.launch();

  // Create a new page
  const page = await browser.newPage();

  // Set viewport width and height
  await page.setViewport({ width: 800, height: 480 });

  const website_url = 'http://jiaqi-desktop.local:3000/d/sPcihT2Vk/solar-e-ink?orgId=1&kiosk';

  // Open URL in current page
  await page.goto(website_url, { waitUntil: 'networkidle0' });

  // Capture screenshot
  await page.screenshot({
    path: 'screenshot.jpg',
  });

  // Close the browser instance
  await browser.close();
})();
