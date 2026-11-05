// Unlock the calendar page in Chromium, jump to a month, screenshot it.
// Usage: FS_CAL_PASS=... NODE_PATH=$(npm root -g) node smoke_test.js <url> <YYYY-MM> <out.png> [schoolKey ...]
// With school keys, only those schools (plus all exams) stay switched on.
const { chromium } = require('playwright');
(async () => {
  const [url, month, out, ...only] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 2400 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(url);
  await page.fill('#pw', process.env.FS_CAL_PASS);
  await page.click('#gateBtn');
  await page.waitForSelector('#schoolChips button', { timeout: 20000 });
  if (only.length) {
    // every click re-renders the chips, so look each one up fresh
    const keys = await page.$$eval('#schoolChips button', bs => bs.map(b => b.dataset.k));
    for (const k of keys) if (!only.includes(k)) await page.click(`#sc-${k}`);
  }
  await page.click('#vMonth');
  const target = month.split('-').map(Number);
  for (let i = 0; i < 24; i++) {
    const [y, m] = (await page.textContent('#mTitle')).match(/\d+/g).map(Number);
    const diff = (target[0] - y) * 12 + (target[1] - m);
    if (!diff) break;
    await page.click(diff > 0 ? '#next' : '#prev');
  }
  await page.screenshot({ path: out, fullPage: true });
  console.log(`title=${await page.textContent('#mTitle')} events=${await page.locator('.ev').count()} errors=${JSON.stringify(errors)}`);
  await browser.close();
  if (errors.length) process.exit(1);
})();
