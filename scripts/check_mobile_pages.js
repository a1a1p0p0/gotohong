const { chromium } = require("../mobile/node_modules/playwright");

const pages = [
  ["/", "五行行业动能"],
  ["/free-year", "年度免费分析"],
  ["/free-week", "本周免费分析"],
  ["/categories", "行业大类"],
  ["/astock", "A 股板块五行"],
  ["/ranking", "行业方案"],
  ["/subcategory", "细分行业付费分析"],
  ["/payment", "微信扫码支付"],
  ["/user", "用户历史"],
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  let passed = 0;
  for (const [path, expectedText] of pages) {
    const response = await page.goto(`http://127.0.0.1:3000${path}`, { waitUntil: "load", timeout: 60000 });
    const body = await page.locator("body").innerText();
    const ok = response?.status() === 200 && body.includes(expectedText);
    if (ok) passed += 1;
    console.log(`${path}: ${ok ? "OK" : "FAIL"} status=${response?.status()} text=${expectedText}`);
  }
  console.log(`SUMMARY: ${passed}/${pages.length}`);
  await browser.close();
  if (passed !== pages.length) process.exit(1);
})();
