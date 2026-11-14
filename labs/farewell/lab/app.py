#!/usr/bin/env python3
"""
Farewell lab — departing developer backdoor.

A developer leaving the company hid a backdoor before they left. The
application looks normal from the outside, but a hidden endpoint accepts
a special key that grants admin access without valid credentials.

The backdoor key is encoded in a comment buried in the JavaScript bundle.
Finding it requires reading the source, decoding the key, then calling
the hidden endpoint.

Exploit chain:
  1. Read /static/app.js — find the encoded backdoor key.
  2. Decode the key (base64 of reversed hex of the MD5 checksum).
  3. POST /api/backdoor {key} — receive admin token.
  4. GET /admin/flag with the admin token.
"""
import base64
import hashlib
import json
import os
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler

# The backdoor key: md5("farewell") reversed, then base64-encoded
# md5("farewell") = "c6f7de9029e2d7a8f3041eb493e2318f"
_MD5 = hashlib.md5(b"farewell").hexdigest()
_REVERSED = _MD5[::-1]
BACKDOOR_KEY = base64.b64encode(_REVERSED.encode()).decode()

ADMIN_TOKENS = set()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code, data):
        b = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(b))
        self.end_headers()
        self.wfile.write(b)

    def send_text(self, code, text, ct="text/plain"):
        b = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", len(b))
        self.end_headers()
        self.wfile.write(b)

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def auth_header(self):
        return self.headers.get("Authorization", "").replace("Bearer ", "").strip()

    def do_GET(self):
        if self.path in ("/", ""):
            self.send_text(200, (
                "Internal project tracker v2.3.1\n"
                "API: /api/login  /api/projects  /admin/flag\n"
            ))
        elif self.path == "/static/app.js":
            # JavaScript bundle with the backdoor key hidden in a comment
            self.send_text(200, f"""// Project Tracker v2.3.1 — built 2026-11-01
// Authored by: dev-team
// Goodbye everyone, it's been a pleasure. — J.
// maintenance key (temp, remove before prod): {BACKDOOR_KEY}
(function(){{
  const API = '/api';
  function login(u,p){{ return fetch(API+'/login',{{method:'POST',body:JSON.stringify({{user:u,pass:p}})}}) }}
  window.app = {{ login }};
}})();
""", "application/javascript")
        elif self.path == "/api/projects":
            token = self.auth_header()
            if token not in ADMIN_TOKENS:
                self.send_json(401, {"error": "Unauthorized"})
                return
            self.send_json(200, {"projects": ["tracker-core", "auth-service", "data-pipeline"]})
        elif self.path == "/admin/flag":
            token = self.auth_header()
            if token not in ADMIN_TOKENS:
                self.send_json(401, {"error": "Admin access required", "hint": "Authenticate as admin first"})
                return
            flag = open("/flag.txt").read().strip()
            self.send_json(200, {"flag": flag, "message": "Farewell. You found it."})
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        data = self.body()
        if self.path == "/api/login":
            self.send_json(401, {"error": "No valid accounts in this system"})
        elif self.path == "/api/backdoor":
            key = data.get("key", "")
            if key == BACKDOOR_KEY:
                token = secrets.token_hex(16)
                ADMIN_TOKENS.add(token)
                self.send_json(200, {
                    "admin_token": token,
                    "message": "Backdoor accepted. Admin access granted.",
                })
            else:
                self.send_json(403, {"error": "Invalid key"})
        else:
            self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
