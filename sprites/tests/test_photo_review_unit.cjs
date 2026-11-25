/* Fast, dependency-free DOM simulation for the browser-local photo pane.
 * A separate Playwright suite checks actual browser layout where Chromium is available.
 */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '../kit/demo/page.html'), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
const script = scripts.at(-1)?.[1];
assert.match(script || '', /Browser-local photo\/video review/);

const charts = {
  '1': { label: 'Chart 1', all: [
    { slot: 'ex1', name: 'Toe touch' },
    { slot: 'ex2', name: 'Sit-up' },
    { slot: 'ex3', name: 'Back extension' },
  ] },
  '2': { label: 'Chart 2', all: [{ slot: 'ex1', name: 'Toe touch outside feet' }] },
};
const inventory = { charts, default_chart: '1' };

function harness(fetchFails = false) {
  const objectURLs = new Map(), revoked = [], listeners = {};
  class Element {
    constructor(tag, id = '') {
      this.tag = tag; this.id = id; this.children = [];
      this._value = ''; this._textContent = ''; this.events = {}; this.attrs = {};
      this.dataset = {}; this.hidden = false; this.disabled = false; this.files = [];
      this.naturalWidth = 32; this.naturalHeight = 32;
    }
    get value() { return this._value; }
    set value(v) { this._value = String(v); }
    get textContent() { return this.children.length ? this.children.map((c) => c.textContent).join('') : this._textContent; }
    set textContent(v) { this._textContent = String(v); this.children = []; }
    get options() { return this.children.filter((c) => c.tag === 'option'); }
    set src(v) {
      this._src = v;
      if (this.id === 'photo-image' && this.onload) queueMicrotask(() => this.onload());
    }
    get src() { return this._src; }
    append(...children) {
      this.children.push(...children);
      if (this.tag === 'select' && this.children.length && !this._value) this._value = this.children[0].value;
    }
    replaceChildren(...children) { this.children = []; this._value = this.tag === 'select' ? '' : this._value; this.append(...children); }
    setAttribute(key, value) { this.attrs[key] = String(value); }
    getAttribute(key) { return this.attrs[key]; }
    removeAttribute(key) { delete this.attrs[key]; if (key === 'src') this._src = ''; }
    addEventListener(key, fn) { this.events[key] = fn; }
    fire(key) { if (this.events[key]) this.events[key](); }
    pause() { this.paused = true; }
    load() {}
  }
  const ids = [
    'photo-chart', 'photo-exercise', 'photo-files', 'photo-stage',
    'photo-image', 'photo-video', 'photo-empty', 'photo-media-list',
    'photo-status', 'photo-background',
  ];
  const elements = Object.fromEntries(ids.map((id) => [id, new Element('div', id)]));
  elements['photo-chart'].tag = 'select';
  elements['photo-exercise'].tag = 'select';
  elements['photo-background'].tag = 'select';
  elements['photo-background'].value = 'track';
  const document = {
    getElementById(id) { return elements[id]; },
    createElement(tag) {
      if (tag === 'canvas') {
        return {
          width: 0, height: 0,
          getContext() {
            let source = null;
            return {
              drawImage(img) { source = img; },
              getImageData() {
                const f = objectURLs.get(source.src);
                return { data: Uint8ClampedArray.from(f?.testAlpha ? [0, 0, 0, 0] : [0, 0, 0, 255]) };
              },
            };
          },
        };
      }
      return new Element(tag);
    },
  };
  let objectID = 0, writes = 0;
  const context = {
    document,
    fetch: async (url) => {
      assert.equal(url, 'data.json');
      if (fetchFails) return { ok: false };
      return { ok: true, json: async () => inventory };
    },
    URL: {
      createObjectURL(file) { const url = 'blob:test/' + ++objectID; objectURLs.set(url, file); return url; },
      revokeObjectURL(url) { revoked.push(url); objectURLs.delete(url); },
    },
    window: { addEventListener(key, fn) { listeners[key] = fn; } },
    console,
    queueMicrotask,
  };
  // No network writes, image generation, uploads, or filesystem writes can be
  // issued by this constrained execution context.
  vm.runInNewContext(script, context, { filename: 'photo-review.js' });
  return { elements, listeners, revoked, get writes() { return writes; }, ready: () => new Promise((resolve) => setImmediate(resolve)) };
}

test('all chart/exercise options derive from inventory; empty movements are honest', async () => {
  const h = harness(); await h.ready();
  const c = h.elements['photo-chart'], e = h.elements['photo-exercise'];
  assert.deepEqual(c.options.map((o) => o.textContent), ['Chart 1', 'Chart 2']);
  assert.deepEqual(e.options.map((o) => o.textContent), ['Toe touch', 'Sit-up', 'Back extension']);
  assert.match(h.elements['photo-status'].textContent, /No photographic media imported/);
  c.value = '2'; c.fire('change');
  assert.deepEqual(e.options.map((o) => o.textContent), ['Toe touch outside feet']);
  assert.equal(h.elements['photo-media-list'].children.length, 0);
});

test('alpha PNG and opaque still are distinguished, and backgrounds switch without uploads', async () => {
  const h = harness(); await h.ready();
  const f = h.elements['photo-files'], list = h.elements['photo-media-list'];
  f.files = [
    { name: 'standing-alpha.png', type: 'image/png', testAlpha: true },
    { name: 'opaque-photo.png', type: 'image/png', testAlpha: false },
  ];
  f.fire('change'); await h.ready();
  assert.equal(list.children.length, 2);
  assert.match(h.elements['photo-status'].textContent, /opaque photograph/);
  list.children[0].fire('click'); await h.ready();
  assert.match(h.elements['photo-status'].textContent, /transparent pixels verified/);
  const b = h.elements['photo-background'];
  b.value = 'studio'; b.fire('change');
  assert.equal(h.elements['photo-stage'].dataset.scene, 'studio');
  b.value = 'dark'; b.fire('change');
  assert.equal(h.elements['photo-stage'].dataset.scene, 'dark');
  const e = h.elements['photo-exercise'];
  e.value = 'ex2'; e.fire('change'); assert.equal(list.children.length, 0);
  e.value = 'ex1'; e.fire('change'); assert.equal(list.children.length, 2);
  assert.equal(h.writes, 0);
  h.listeners.beforeunload();
  assert.equal(h.revoked.length, 2);
});

test('videos are not recolored or uploaded, and untrusted filenames stay plain text', async () => {
  const h = harness(); await h.ready();
  const f = h.elements['photo-files'];
  f.files = [{ name: 'motion.mp4', type: 'video/mp4' }];
  f.fire('change');
  assert.equal(h.elements['photo-video'].hidden, false);
  assert.match(h.elements['photo-video'].src, /^blob:/);
  assert.match(h.elements['photo-status'].textContent, /embedded scenery is not removed/);
  f.files = [{ name: '<img onerror=alert(1)>.png', type: 'image/png', testAlpha: true }];
  f.fire('change'); await h.ready();
  const list = h.elements['photo-media-list'];
  assert.equal(list.children.length, 2);
  assert.equal(list.children[1].textContent, '<img onerror=alert(1)>.png');
  assert.equal(list.children[1].children.length, 0);
  assert.equal(h.writes, 0);
});

test('failed inventory disables import and gives a readable fallback', async () => {
  const h = harness(true); await h.ready();
  assert.match(h.elements['photo-status'].textContent, /inventory unavailable/);
  assert.equal(h.elements['photo-files'].disabled, true);
});
