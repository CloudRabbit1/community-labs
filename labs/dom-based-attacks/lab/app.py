#!/usr/bin/env python3
"""
DOM-Based XSS via innerHTML sink.

The /reflect endpoint takes a q= query parameter and injects it
directly into an HTML page via innerHTML without sanitization.
An attacker injects a script payload that runs in the victim's
browser context, stealing cookies or the flag from /api/flag.
"""
import json
import secrets
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

SESSIONS = {}


def html_page(title: str, body: str) -> bytes:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
{body}
</body>
</html>""".encode()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_html(self, code: int, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, code: int, data: dict, extra_headers=None):
        b = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def get_session(self):
        for part in self.headers.get("Cookie", "").split(";"):
            part = part.strip()
            if part.startswith("session="):
                return SESSIONS.get(part[8:])
        return None

    def read_body(self) -> bytes:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            page = html_page("Search", """
<h1>Search</h1>
<form action="/reflect">
  <input type="text" name="q" placeholder="Search...">
  <button type="submit">Search</button>
</form>
<div id="results"></div>
<script>
  // Displays the search query in the results div
  const q = new URLSearchParams(location.search).get('q') || '';
  document.getElementById('results').innerHTML = q;
</script>
""")
            self.send_html(200, page)
            return

        if path == "/reflect":
            q = params.get("q", [""])[0]
            # Vulnerable: q is injected directly into innerHTML without sanitization
            body = f"""<h1>Search Results</h1>
<div id="results"></div>
<script>
  document.getElementById('results').innerHTML = {json.dumps(q)};
</script>"""
            page = html_page("Results", body)
            self.send_html(200, page)
            return

        if path == "/api/flag":
            user = self.get_session()
            if not user:
                self.send_json(401, {"error": "Unauthorized"})
                return
            flag = open("/flag.txt").read().strip()
            self.send_json(200, {"flag": flag, "user": user})
            return

        if path == "/exfil":
            # Simulated attacker-controlled receiver
            d = params.get("d", [""])[0]
            self.send_json(200, {"received": d[:200]})
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/login":
            try:
                data = json.loads(self.read_body())
            except Exception:
                self.send_json(400, {"error": "Invalid JSON"})
                return
            if data.get("username") == "admin" and data.get("password") == "admin":
                token = secrets.token_hex(16)
                SESSIONS[token] = "admin"
                self.send_json(200, {"ok": True, "session": token},
                               extra_headers={"Set-Cookie": f"session={token}; HttpOnly"})
                return
            self.send_json(401, {"error": "Invalid credentials"})
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
