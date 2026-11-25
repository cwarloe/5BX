/* Standalone browser regression for the static Mixer review panel.
 * Run: node --test sprites/tests/test_photo_review.cjs
 * Uses the installed Playwright package and a system Chromium (or Playwright's browser).
 */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const zlib = require('node:zlib');
const { chromium } = require('playwright');

const pageSource = fs.readFileSync(path.join(__dirname, '../kit/demo/page.html'), 'utf8');
const html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">' + pageSource + '</html>';
const slots = ['ex1', 'ex2', 'ex3', 'ex4', 'run', 'jump'];
const exerciseList = (prefix) => slots.map((slot, i) => ({ slot, name: prefix + ' movement ' + (i + 1), built: false }));
const fixture = {
  frame: [640, 360], floor: 305, default_chart: '1', layers: [], props: [], regions: {},
  charts: {
    '1': { label: 'Chart 1', status: 'planned', all: exerciseList('One'), slots: {}, order: [], prompts_ready: false },
    '2': { label: 'Chart 2', status: 'planned', all: exerciseList('Two'), slots: {}, order: [], prompts_ready: false },
  },
};

// Generate two real PNG fixtures in memory; no binary art is committed to Git.
function crc32(buf) {
  let c = -1;
  for (const b of buf) {
    c ^= b;
    for (let j = 0; j < 8; j++) c = (c >>> 1) ^ ((c & 1) ? 0xedb88320 : 0);
  }
  return (c ^ -1) >>> 0;
}
function chunk(tag, payload) {
  const body = Buffer.concat([Buffer.from(tag), payload]);
  const head = Buffer.alloc(4); head.writeUInt32BE(payload.length);
  const tail = Buffer.alloc(4); tail.writeUInt32BE(crc32(body));
  return Buffer.concat([head, body, tail]);
}
function png(alpha) {
  const header = Buffer.alloc(13);
  header.writeUInt32BE(2, 0); header.writeUInt32BE(2, 4);
  header[8] = 8; header[9] = 6; // RGBA
  const pixel = [50, 130, 220, 255], transparent = [0, 0, 0, 0];
  const a = alpha ? transparent : pixel;
  const row1 = Buffer.from([0, ...pixel, ...pixel]);
  const row2 = Buffer.from([0, ...pixel, ...a]);
  return Buffer.concat([
    Buffer.from('89504e470d0a1a0a', 'hex'),
    chunk('IHDR', header),
    chunk('IDAT', zlib.deflateSync(Buffer.concat([row1, row2]))),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}
const file = (name, buffer) => ({ name, mimeType: 'image/png', buffer });

let server, browser, base, unsupported, browserError;
test.before(async () => {
  server = http.createServer((req, res) => {
    if (req.url === '/data.json' && !unsupported) {
      res.writeHead(200, { 'content-type': 'application/json' }); res.end(JSON.stringify(fixture));
    } else if (req.url === '/') {
      res.writeHead(200, { 'content-type': 'text/html' }); res.end(html);
    } else {
      res.writeHead(404); res.end('Not found');
    }
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  base = 'http://127.0.0.1:' + server.address().port;
  try {
    browser = await chromium.launch({ headless: true });
  } catch (_) {
    try {
      browser = await chromium.launch({ headless: true, executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] });
    } catch (err) {
      browserError = err.message.split('\n')[0];
    }
  }
});
test.after(async () => {
  if (browser) await browser.close();
  if (server) await new Promise((resolve) => server.close(resolve));
});
async function openPage(viewport) {
  const page = await browser.newPage({ viewport: viewport || { width: 1200, height: 850 } });
  const writes = [];
  page.on('request', (request) => {
    if (!['GET', 'HEAD'].includes(request.method())) writes.push(request.method() + ' ' + request.url());
  });
  await page.route('**/*', (route) => {
    if (route.request().url().startsWith(base)) route.continue();
    else route.abort();
  });
  await page.goto(base);
  // Native <option> elements exist in the DOM but are not considered "visible"
  // by Playwright until the select popup is open.
  await page.locator('#photo-exercise option').first().waitFor({ state: 'attached' });
  return { page, writes };
}
async function captureReview(page, fileName) {
  const folder = process.env.MIXER_QA_SCREENSHOT_DIR;
  if (!folder) return;
  fs.mkdirSync(folder, { recursive: true });
  await page.screenshot({ path: path.join(folder, fileName), fullPage: true });
}

test('chart inventory and existing Mixer controls remain available', async (t) => {
  if (!browser) return t.skip('Chromium unavailable: ' + browserError);
  const { page, writes } = await openPage();
  try {
    assert.deepEqual(await page.locator('#photo-chart option').allTextContents(), ['Chart 1', 'Chart 2']);
    assert.match(await page.locator('#photo-status').textContent(), /No photographic media imported/);
    await page.locator('#photo-chart').selectOption('2');
    assert.equal(await page.locator('#photo-exercise option').count(), 6);
    assert.match(await page.locator('#photo-exercise option').first().textContent(), /Two movement 1/);
    assert.equal(await page.locator('#chart option').count(), 2);
    assert.equal(await page.locator('#hues input[type="range"]').count(), 3);
    assert.equal(await page.locator('#presets button').count(), 4);
    await captureReview(page, 'desktop-workout-mixer.png');
    await page.locator('#play').click();
    assert.equal(await page.locator('#play').textContent(), 'Play');
    assert.deepEqual(writes, []);
  } finally { await page.close(); }
});

test('transparent and opaque image imports are distinguished and scoped by movement', async (t) => {
  if (!browser) return t.skip('Chromium unavailable: ' + browserError);
  const { page, writes } = await openPage();
  try {
    await page.locator('#photo-files').setInputFiles([
      file('alpha.png', png(true)), file('opaque.png', png(false)),
    ]);
    assert.equal(await page.locator('#photo-media-list button').count(), 2);
    await page.waitForFunction(() => document.querySelector('#photo-status')?.textContent.includes('opaque photograph'));
    await page.locator('#photo-media-list button').first().click();
    await page.waitForFunction(() => document.querySelector('#photo-status')?.textContent.includes('transparent pixels verified'));
    await page.locator('#photo-background').selectOption('studio');
    assert.equal(await page.locator('#photo-stage').getAttribute('data-scene'), 'studio');
    await page.locator('#photo-background').selectOption('dark');
    assert.equal(await page.locator('#photo-stage').getAttribute('data-scene'), 'dark');
    await page.locator('#photo-exercise').selectOption('ex2');
    assert.equal(await page.locator('#photo-media-list button').count(), 0);
    await page.locator('#photo-exercise').selectOption('ex1');
    assert.equal(await page.locator('#photo-media-list button').count(), 2);
    await page.locator('#photo-clear').click();
    assert.equal(await page.locator('#photo-media-list button').count(), 0);
    assert.equal(await page.locator('#photo-clear').isDisabled(), true);
    assert.deepEqual(writes, []);
  } finally { await page.close(); }
});

test('video stays in browser, filenames are treated as text, and layout fits a phone', async (t) => {
  if (!browser) return t.skip('Chromium unavailable: ' + browserError);
  const { page, writes } = await openPage({ width: 390, height: 844 });
  try {
    await page.locator('#photo-files').setInputFiles([{
      name: 'exercise-video.mp4', mimeType: 'video/mp4', buffer: Buffer.from('test video bytes'),
    }]);
    assert.equal(await page.locator('#photo-video').isVisible(), true);
    assert.equal(await page.locator('#photo-video').getAttribute('controls'), '');
    assert.match(await page.locator('#photo-video').getAttribute('src'), /^blob:/);
    await page.locator('#photo-files').setInputFiles(file('<img src=x onerror=alert(1)>.png', png(true)));
    assert.equal(await page.locator('#photo-media-list button').count(), 2);
    assert.equal(await page.locator('#photo-media-list img').count(), 0);
    assert.match(await page.locator('#photo-media-list').textContent(), /<img src=x/);
    await captureReview(page, 'mobile-photographic-review.png');
    const sizes = await page.evaluate(() => ({
      document: document.documentElement.scrollWidth,
      viewport: document.documentElement.clientWidth,
      panelRight: document.querySelector('#photo-background').closest('.panel').getBoundingClientRect().right,
      controlsRight: Math.max(document.querySelector('#photo-background').getBoundingClientRect().right, document.querySelector('#photo-clear').getBoundingClientRect().right),
      overflowing: [...document.querySelectorAll('body *')].filter((node) => node.getBoundingClientRect().right > document.documentElement.clientWidth + 1).slice(0, 8).map((node) => ({
        element: node.tagName.toLowerCase(), id: node.id, class: node.className?.baseVal ?? node.className,
        right: Math.round(node.getBoundingClientRect().right),
      })),
    }));
    assert.ok(sizes.document <= sizes.viewport + 1, JSON.stringify(sizes));
    assert.ok(sizes.controlsRight <= sizes.panelRight + 1, JSON.stringify(sizes));
    assert.deepEqual(writes, []);
  } finally { await page.close(); }
});

test('missing inventory gives a readable fallback without breaking review links', async (t) => {
  if (!browser) return t.skip('Chromium unavailable: ' + browserError);
  unsupported = true;
  const page = await browser.newPage();
  try {
    await page.route('**/*', (route) => route.request().url().startsWith(base) ? route.continue() : route.abort());
    await page.goto(base);
    await page.waitForFunction(() => document.querySelector('#photo-status')?.textContent.includes('inventory unavailable'));
    assert.equal(await page.locator('#photo-files').isDisabled(), true);
    assert.equal(await page.locator('#photographic-review a').count(), 3);
  } finally {
    unsupported = false;
    await page.close();
  }
});
