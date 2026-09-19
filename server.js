/* Static file server for local development and the test suite.

   node server.js            serve this directory on :8080
   PORT=3000 node server.js  serve on another port

   The app fetches its data file, so it needs HTTP rather than file://.
   No dependencies — the app itself has no backend and this only exists so
   there is something to open it with. */

const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = process.env.PORT || 8080;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  let file = path.join(ROOT, url === '/' ? 'index.html' : url);

  // Keep the response inside the served directory.
  if (!file.startsWith(ROOT)) {
    res.writeHead(403).end('Forbidden');
    return;
  }

  fs.stat(file, (err, stat) => {
    if (!err && stat.isDirectory()) file = path.join(file, 'index.html');

    fs.readFile(file, (err, body) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain' }).end('Not found');
        return;
      }
      res.writeHead(200, {
        'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream',
        // The service worker decides what is cached; don't let the dev server
        // serve a stale copy on top of it.
        'Cache-Control': 'no-cache',
      });
      res.end(body);
    });
  });
});

server.listen(PORT, () => {
  console.log(`5BX on http://localhost:${PORT}/`);
});
