// Renders the two value stream map figures to PNG (4x) and vector PDF.
// Requires Node.js and Playwright:  npm install playwright && npx playwright install chromium
// Usage: node maps/render_maps.js
const { chromium } = require('playwright');
const path = require('path');
const jobs = [['figure1_case_a_map.html', 'Figure1_DDVSM_CaseA'], ['figure3_case_b_map.html', 'Figure3_DDVSM_CaseB']];
(async () => {
  const b = await chromium.launch();
  for (const [src, name] of jobs) {
    const p = await b.newPage({ viewport: { width: 1700, height: 1000 }, deviceScaleFactor: 4 });
    await p.goto('file://' + path.resolve(__dirname, src));
    const w = Math.ceil(await p.evaluate(() => document.body.getBoundingClientRect().width));
    await p.setViewportSize({ width: w, height: 1000 });
    const h = Math.ceil(await p.evaluate(() => document.body.scrollHeight));
    await p.setViewportSize({ width: w, height: h });
    const out = path.resolve(__dirname, '..', 'figures');
    await p.screenshot({ path: path.join(out, name + '.png'), fullPage: true });
    await p.pdf({ path: path.join(out, name + '.pdf'), width: w + 'px', height: (h + 2) + 'px', printBackground: true, pageRanges: '1' });
    console.log('rendered', name);
  }
  await b.close();
})();
