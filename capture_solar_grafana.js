const puppeteer = require('puppeteer-core');

(async () => {
  // Create a browser instance
  console.log("launching chromium...");
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {

    console.log("opening page...");

    // Create a new page
    const page = await browser.newPage();

    // Set viewport width and height
    await page.setViewport({ width: 1872, height: 1404, deviceScaleFactor: 3 });

    const website_url = 'https://grafana.jiaqiwu.io/d/uxVUaO2Vz/solar?orgId=1&refresh=5s&kiosk';

    // Open URL in current page
    await page.goto(website_url, { waitUntil: 'networkidle0' });

    console.log("saving screenshot to screenshot.png...");
    // Capture screenshot
    await page.screenshot({
      path: 'screenshot.png',
    });
  } catch (e) {
    console.log(e);
  } finally {
    // Close the browser instance
    await browser.close();
  }
})();
