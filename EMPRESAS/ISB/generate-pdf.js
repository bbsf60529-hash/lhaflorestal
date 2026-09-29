const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    headless: true,
  });

  const page = await browser.newPage();

  // Set viewport to A4 dimensions
  await page.setViewportSize({ width: 1200, height: 1600 });

  // Read HTML file
  const htmlPath = path.resolve('./relatorios/isb-12.html');
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');

  // Set HTML content
  await page.setContent(htmlContent, { waitUntil: 'networkidle' });

  // Wait for all images to load
  await page.waitForLoadState('networkidle');

  // Generate PDF with print settings
  const pdfPath = './relatorios/isb-12.pdf';
  await page.pdf({
    path: pdfPath,
    format: 'A4',
    margin: { top: '10mm', right: '10mm', bottom: '10mm', left: '10mm' },
    printBackground: true,
    preferCSSPageSize: true,
    scale: 1.0,
  });

  console.log(`✅ PDF generated: ${pdfPath}`);
  
  // Get file size
  const stats = fs.statSync(pdfPath);
  console.log(`📄 File size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);

  await browser.close();
})();
