// Build the downloadable A4 PDFs for every 5-minute revision sheet.
// One-time setup (in the repo folder):  npm i -D playwright  &&  npx playwright install chromium
// Then run:                             node scripts/revision-pdf.cjs
// Each revision/<book>/<sheet>.html gets a matching <sheet>.pdf next to it.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const root = path.join(__dirname, '..', 'revision');
const sheets = fs.readdirSync(root, { withFileTypes: true })
  .filter(d => d.isDirectory() && d.name !== 'assets')
  .flatMap(d => fs.readdirSync(path.join(root, d.name))
    .filter(f => f.endsWith('.html'))
    .map(f => path.join(root, d.name, f)));

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const file of sheets) {
    await page.goto(pathToFileURL(file).href, { waitUntil: 'load' });
    await page.waitForFunction(() => document.documentElement.classList.contains('math-ready'));
    await page.evaluate(() => document.fonts.ready);
    await page.emulateMedia({ media: 'print' });
    const out = file.replace(/\.html$/, '.pdf');
    await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
    const pages = (fs.readFileSync(out, 'latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
    const okPages = file.endsWith("all-chapters.html") ? pages > 1 : pages <= 2;
    console.log(`${okPages ? 'ok  ' : 'WARN'} ${path.relative(root, out)} (${pages} page${pages === 1 ? '' : 's'})`);
  }
  await browser.close();
})();
