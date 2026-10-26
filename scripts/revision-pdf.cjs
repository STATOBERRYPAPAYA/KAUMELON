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
  const browser = await chromium.launch(process.env.REVISION_BROWSER_CHANNEL ? {channel:process.env.REVISION_BROWSER_CHANNEL} : {});
  const page = await browser.newPage();
  for (const file of sheets.filter(file => !process.env.REVISION_ONLY || file.includes(process.env.REVISION_ONLY))) {
    await page.goto(pathToFileURL(file).href, { waitUntil: 'load' });
    await page.waitForFunction(() => document.documentElement.classList.contains('math-ready'));
    await page.evaluate(() => document.fonts.ready);
    await page.emulateMedia({ media: 'print' });
    await page.evaluate(() => { document.querySelectorAll('.fxgrid .fx').forEach(box => { const math=box.querySelector('.katex-display'); if(math && math.scrollWidth > math.clientWidth+2) box.classList.add('wide'); }); });
    await page.evaluate(() => { document.querySelectorAll('.katex-display').forEach(display => { const math=display.querySelector('.katex'); if(!math)return; const available=display.clientWidth; const natural=Math.max(math.scrollWidth, math.getBoundingClientRect().width); if(natural>available && available>0) math.style.fontSize=(parseFloat(getComputedStyle(math).fontSize)*(available-4)/natural)+'px'; }); });
    const out = file.replace(/\.html$/, '.pdf');
    await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true, displayHeaderFooter:true, headerTemplate:'<span></span>', footerTemplate:'<div style="font:8px Arial;color:#496252;width:100%;padding:0 38px;display:flex;justify-content:space-between"><span>KAU Me-LON · Agricultural Statistics · agrinoteskau.com</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' });
    const mathErrors = await page.locator('.katex-error').count();
    if(mathErrors) throw Error(`${file}: ${mathErrors} formula rendering errors`);
    const pages = (fs.readFileSync(out, 'latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
    const okPages = file.endsWith("all-chapters.html") ? pages > 1 : pages <= 3;
    console.log(`${okPages ? 'ok  ' : 'WARN'} ${path.relative(root, out)} (${pages} page${pages === 1 ? '' : 's'})`);
  }
  await browser.close();
})();
