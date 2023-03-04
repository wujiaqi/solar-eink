const puppeteer = require('puppeteer-core');

(async () => {
  // Create a browser instance
  console.log("launching chromium...")
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  console.log("opening page...")

  // Create a new page
  const page = await browser.newPage();

  // Set viewport width and height
  await page.setViewport({ width: 800, height: 480 });

  const website_url = 'http://jiaqi-desktop.local:3000/d/sPcihT2Vk/solar-e-ink?orgId=1&kiosk';

  // Open URL in current page
  await page.goto(website_url, { waitUntil: 'networkidle0' });

  console.log("saving screenshot to screenshot.png...")
  // Capture screenshot
  await page.screenshot({
    path: 'screenshot.png',
  });

  // Close the browser instance
  await browser.close();
})();
