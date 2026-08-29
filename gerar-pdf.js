const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.goto('file:///home/user/lhaflorestal/relatorio-isb09-valmet-1280.html', { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'print' });
  await page.evaluate(() => Promise.all(Array.from(document.images).map(i => i.complete ? null : i.decode().catch(() => null))));
  await page.pdf({
    path: '/home/user/lhaflorestal/Relatorio-Manutencao-ISB09-Valmet-1280.pdf',
    format: 'A4',
    printBackground: true,
    margin: { top: '0mm', bottom: '0mm', left: '0mm', right: '0mm' },
    scale: 1,
  });
  await browser.close();
  console.log('pdf gerado');
})();
