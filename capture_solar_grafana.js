
const puppeteer = require('puppeteer-core');
const commander = require('commander');

(async () => {
  commander
    .version('1.0.0', '-v, --version')
    .usage('[OPTIONS]...')
    .option('-h, --height <value>', 'window height', 600)
    .option('-w, --width <value>', 'window width', 800)
    .parse(process.argv);

  const options = commander.opts();
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
    await page.setViewport({ width: options.width, height: options.height, deviceScaleFactor: 1 });

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
