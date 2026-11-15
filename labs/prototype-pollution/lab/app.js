/**
 * Prototype Pollution lab.
 *
 * A note-sharing API merges user-supplied JSON into internal objects using a
 * naive recursive merge. When the JSON contains __proto__ keys, those values
 * land on Object.prototype and affect every object in the process.
 *
 * The admin check reads isAdmin from the request object. Because Object.prototype
 * is shared by all objects, polluting isAdmin=true lets any user pass the check.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const FLAG_FILE = '/flag.txt';
const PORT = 8080;

/**
 * Vulnerable deep merge. Never use in production.
 * Merges src into dst, following nested keys including __proto__.
 */
function merge(dst, src) {
  for (const key of Object.keys(src)) {
    if (typeof src[key] === 'object' && src[key] !== null) {
      if (!dst[key]) dst[key] = {};
      merge(dst[key], src[key]);
    } else {
      dst[key] = src[key];
    }
  }
  return dst;
}

// In-memory note store
const notes = {};

function readBody(req) {
  return new Promise((resolve) => {
    let data = '';
    req.on('data', chunk => { data += chunk; });
    req.on('end', () => resolve(data));
  });
}

function sendJSON(res, code, obj) {
  const body = JSON.stringify(obj, null, 2);
  res.writeHead(code, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = url.pathname;

  if (req.method === 'GET' && pathname === '/') {
    return sendJSON(res, 200, {
      app: 'NoteShare API v2.1',
      note: 'Prototype Pollution: __proto__ in merge target poisons Object.prototype',
      endpoints: [
        'GET  /notes          list all notes',
        'POST /notes          save a note (body: {"title":"...","body":"..."})',
        'POST /notes/merge    merge options into a note (body: {"id":"...","options":{...}})',
        'GET  /admin/flag     read the flag (admin only)',
      ],
    });
  }

  if (req.method === 'GET' && pathname === '/notes') {
    return sendJSON(res, 200, { notes: Object.entries(notes).map(([id, n]) => ({ id, title: n.title })) });
  }

  if (req.method === 'POST' && pathname === '/notes') {
    let body;
    try { body = JSON.parse(await readBody(req)); } catch { return sendJSON(res, 400, { error: 'Invalid JSON' }); }
    const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    notes[id] = { title: body.title || 'Untitled', body: body.body || '' };
    return sendJSON(res, 201, { id, message: 'Note saved' });
  }

  // Vulnerable endpoint: merges user JSON into the note options object
  if (req.method === 'POST' && pathname === '/notes/merge') {
    let body;
    try { body = JSON.parse(await readBody(req)); } catch { return sendJSON(res, 400, { error: 'Invalid JSON' }); }
    const note = notes[body.id];
    if (!note) return sendJSON(res, 404, { error: 'Note not found' });

    if (!note.options) note.options = {};
    merge(note.options, body.options || {});           // <-- vulnerable merge
    return sendJSON(res, 200, { message: 'Options merged', options: note.options });
  }

  if (req.method === 'GET' && pathname === '/admin/flag') {
    const ctx = {};   // fresh empty object
    // isAdmin check: ctx itself has no isAdmin, falls back to Object.prototype
    if (!ctx.isAdmin) {
      return sendJSON(res, 403, { error: 'Admin only' });
    }
    const flag = fs.readFileSync(FLAG_FILE, 'utf8').trim();
    return sendJSON(res, 200, { flag });
  }

  return sendJSON(res, 404, { error: 'Not found' });
});

server.listen(PORT, '0.0.0.0', () => {
  process.stdout.write(`NoteShare listening on :${PORT}\n`);
});
