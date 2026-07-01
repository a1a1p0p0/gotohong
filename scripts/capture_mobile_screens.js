const { chromium } = require("../mobile/node_modules/playwright");

const pages = [
  ["/", "home"],
  ["/ranking", "ranking"],
  ["/subcategory", "subcategory"],
  ["/payment", "payment"],
  ["/astock", "astock"],
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  for (const [path, name] of pages) {
    await page.goto(`http://127.0.0.1:3000${path}`, { waitUntil: "load", timeout: 60000 });
    await page.screenshot({ path: `reports/mobile_${name}.png`, fullPage: true });
    console.log(`${path}: reports/mobile_${name}.png`);
  }
  await browser.close();
})();
