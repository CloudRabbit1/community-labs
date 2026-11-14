#!/usr/bin/env python3
"""
PulseMon monitoring dashboard.

Vulnerabilities:
1. Default credentials (admin / monitor123) — discoverable via source comment
2. /api/ping passes user-supplied host to bash without sanitisation — command injection
3. Internal metrics service bound to 127.0.0.1:9090 — reachable only via injected curl

Attack path: enumerate ports -> find :8080 -> login with defaults ->
inject ';cat /flag1.txt' -> discover port 9090 -> inject ';curl http://127.0.0.1:9090/'
"""
import json
import os
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ADMIN_USER = "admin"
ADMIN_PASS = os.environ.get("ADMIN_PASS", "monitor123")

HOSTS = [
    {"name": "web-01",  "ip": "10.0.0.10", "status": "UP"},
    {"name": "db-01",   "ip": "10.0.0.20", "status": "UP"},
    {"name": "cache-01","ip": "10.0.0.30", "status": "DOWN"},
]


def parse_cookies(header: str) -> dict:
    out = {}
    for part in header.split(";"):
        if "=" in part:
            k, _, v = part.partition("=")
            out[k.strip()] = v.strip()
    return out


def parse_form(body: bytes) -> dict:
    return dict(urllib.parse.parse_qsl(body.decode()))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def cookies(self):
        return parse_cookies(self.headers.get("Cookie", ""))

    def authenticated(self):
        return self.cookies().get("auth") == "1"

    def send_html(self, code: int, body: str, extra_headers=None):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def send_json(self, code: int, data: dict):
        b = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def send_redirect(self, loc: str):
        self.send_response(302)
        self.send_header("Location", loc)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/":
            self.send_redirect("/dashboard" if self.authenticated() else "/login")
            return

        if path == "/login":
            self.send_html(200, self.login_page())
            return

        if path == "/logout":
            self.send_response(302)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", "auth=; Path=/; Max-Age=0")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if path == "/dashboard":
            if not self.authenticated():
                self.send_redirect("/login")
                return
            self.send_html(200, self.dashboard_page())
            return

        self.send_html(404, "<h1>Not found</h1>")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        path = urllib.parse.urlparse(self.path).path

        if path == "/login":
            form = parse_form(body)
            if form.get("username") == ADMIN_USER and form.get("password") == ADMIN_PASS:
                self.send_response(302)
                self.send_header("Location", "/dashboard")
                self.send_header("Set-Cookie", "auth=1; Path=/; HttpOnly")
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                self.send_html(200, self.login_page("Invalid credentials"))
            return

        if path == "/api/ping":
            if not self.authenticated():
                self.send_json(401, {"error": "not authenticated"})
                return
            try:
                data = json.loads(body)
                host = data.get("host", "127.0.0.1")
            except Exception:
                self.send_json(400, {"error": "invalid JSON"})
                return
            # VULNERABLE: host concatenated directly into shell command
            result = subprocess.run(
                f"ping -c 1 -W 1 {host}",
                shell=True, capture_output=True, text=True, timeout=15
            )
            output = result.stdout + result.stderr
            self.send_json(200, {"host": host, "output": output})
            return

        self.send_html(404, "<h1>Not found</h1>")

    def login_page(self, error: str = "") -> str:
        # comment intentionally left for discovery: default creds admin/monitor123
        err = f'<p style="color:red">{error}</p>' if error else ""
        return f"""<!doctype html>
<html><head><title>PulseMon</title>
<style>
body{{font-family:monospace;max-width:360px;margin:80px auto;padding:0 16px;background:#111;color:#0f0}}
input{{display:block;width:100%;margin:6px 0;padding:8px;background:#222;color:#0f0;
       border:1px solid #0f0;box-sizing:border-box}}
button{{padding:8px 20px;background:#0f0;color:#000;border:none;cursor:pointer;font-family:monospace}}
</style></head>
<body>
<!-- default credentials: admin / monitor123 -->
<h1>PulseMon v2.1</h1>
<p>Infrastructure monitoring console</p>
{err}
<form method="post" action="/login">
<input name="username" placeholder="username">
<input name="password" type="password" placeholder="password">
<button>Login</button>
</form>
</body></html>"""

    def dashboard_page(self) -> str:
        rows = "".join(
            f'<tr><td>{h["name"]}</td><td>{h["ip"]}</td>'
            f'<td style="color:{"lime" if h["status"]=="UP" else "red"}">{h["status"]}</td></tr>'
            for h in HOSTS
        )
        return f"""<!doctype html>
<html><head><title>PulseMon — Dashboard</title>
<style>
body{{font-family:monospace;max-width:860px;margin:40px auto;padding:0 16px;background:#111;color:#0f0}}
table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #333;padding:8px;text-align:left}}
input{{padding:6px;background:#222;color:#0f0;border:1px solid #0f0;width:260px;font-family:monospace}}
button{{padding:6px 14px;background:#0f0;color:#000;border:none;cursor:pointer;font-family:monospace}}
pre{{background:#222;padding:12px;white-space:pre-wrap;word-break:break-all;min-height:60px}}
a{{color:#0f0}}
</style></head>
<body>
<h1>PulseMon v2.1 &mdash; Dashboard</h1>
<p><a href="/logout">Log out</a></p>

<h2>Monitored Hosts</h2>
<table>
<tr><th>Name</th><th>IP</th><th>Status</th></tr>
{rows}
</table>

<h2>Ping Check</h2>
<input id="host" value="127.0.0.1" placeholder="IP or hostname">
<button onclick="runPing()">Run</button>
<pre id="out">— output will appear here —</pre>

<script>
function runPing() {{
  document.getElementById('out').textContent = 'Running...';
  fetch('/api/ping', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{host: document.getElementById('host').value}})
  }})
  .then(r => r.json())
  .then(d => document.getElementById('out').textContent = d.output)
  .catch(e => document.getElementById('out').textContent = 'Error: ' + e);
}}
</script>
</body></html>"""


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
