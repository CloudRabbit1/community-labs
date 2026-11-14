#!/usr/bin/env python3
"""
TicketDesk support system.

Vulnerability: Python pickle deserialization in session cookie.
Session cookie = base64(pickle.dumps({"username": ..., "role": ...}))
No HMAC, no signature. The server unpickles whatever bytes it receives.

Attack path:
  flag1: craft a session cookie whose pickle payload calls
         subprocess.check_output(['cat', '/flag1.txt'])
         The return value (bytes) is detected and echoed in the response.

  flag2: craft a pickle that returns a dict with 'role':'admin'
         to access the admin panel, which reveals flag2 from /flag2.txt.
"""
import base64
import os
import pickle
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

USERS = {
    "alice": "alice123",
    "admin": os.environ.get("ADMIN_PASS", "admin456"),
}

TICKETS: list = []


def parse_cookies(header: str) -> dict:
    out = {}
    for part in header.split(";"):
        if "=" in part:
            k, _, v = part.partition("=")
            out[k.strip()] = v.strip()
    return out


def parse_form(body: bytes) -> dict:
    return dict(urllib.parse.parse_qsl(body.decode()))


def decode_session(raw: str) -> dict:
    try:
        data = pickle.loads(base64.b64decode(raw))
        if isinstance(data, bytes):
            # RCE: subprocess returned bytes — surface them in the response
            return {"username": "anonymous", "role": "user",
                    "_rce_output": data.decode("utf-8", errors="replace")}
        if isinstance(data, dict):
            return data
        return {"username": str(data), "role": "user"}
    except Exception:
        return {}


def encode_session(data: dict) -> str:
    return base64.b64encode(pickle.dumps(data)).decode()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def cookies(self):
        return parse_cookies(self.headers.get("Cookie", ""))

    def session(self):
        raw = self.cookies().get("session", "")
        if not raw:
            return {}
        return decode_session(raw)

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

    def send_redirect(self, loc: str, extra_headers=None):
        self.send_response(302)
        self.send_header("Location", loc)
        self.send_header("Content-Length", "0")
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        sess = self.session()

        if path == "/":
            if not sess.get("username"):
                self.send_redirect("/login")
            else:
                self.render_dashboard(sess)
            return

        if path == "/login":
            self.send_html(200, self.login_page())
            return

        if path == "/admin":
            if sess.get("role") != "admin":
                self.send_html(403, "<h1>Forbidden</h1>")
                return
            flag2 = open("/flag2.txt").read().strip()
            self.send_html(200, self.admin_page(flag2))
            return

        if path == "/logout":
            self.send_redirect("/login", [("Set-Cookie", "session=; Path=/; Max-Age=0")])
            return

        self.send_html(404, "<h1>Not found</h1>")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        path = urllib.parse.urlparse(self.path).path

        if path == "/login":
            form = parse_form(body)
            username = form.get("username", "")
            password = form.get("password", "")
            if USERS.get(username) == password:
                cookie = encode_session({"username": username,
                                         "role": "admin" if username == "admin" else "user"})
                self.send_redirect("/", [("Set-Cookie", f"session={cookie}; Path=/; HttpOnly")])
            else:
                self.send_html(200, self.login_page("Invalid credentials"))
            return

        if path == "/ticket":
            sess = self.session()
            if not sess.get("username"):
                self.send_redirect("/login")
                return
            form = parse_form(body)
            subject = form.get("subject", "")[:200]
            message = form.get("message", "")[:500]
            if subject:
                TICKETS.append({
                    "user": sess.get("username", "?"),
                    "subject": subject,
                    "message": message,
                })
            self.send_redirect("/")
            return

        self.send_html(404, "<h1>Not found</h1>")

    def login_page(self, error: str = "") -> str:
        err = f'<p class="err">{error}</p>' if error else ""
        return f"""<!doctype html>
<html><head><title>TicketDesk</title>
<style>
body{{font-family:sans-serif;max-width:380px;margin:80px auto;padding:0 16px}}
input{{display:block;width:100%;margin:8px 0;padding:8px;box-sizing:border-box}}
button{{padding:8px 20px;background:#1a56db;color:#fff;border:none;cursor:pointer}}
.err{{color:red}}
</style></head>
<body>
<h1>TicketDesk</h1>
<h2>Log in</h2>
{err}
<form method="post" action="/login">
<input name="username" placeholder="Username">
<input name="password" type="password" placeholder="Password">
<button>Log in</button>
</form>
<p style="font-size:0.85em;color:#666">New user? Register not available — contact admin.</p>
</body></html>"""

    def render_dashboard(self, sess: dict):
        username = sess.get("username", "anonymous")
        role = sess.get("role", "user")
        rce_output = sess.get("_rce_output", "")

        rce_block = ""
        if rce_output:
            safe = rce_output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            rce_block = f'<div class="rce"><strong>Server output:</strong><pre>{safe}</pre></div>'

        all_tickets = TICKETS if role == "admin" else [t for t in TICKETS if t["user"] == username]
        rows = "".join(
            f"<tr><td>{t['user']}</td><td>{t['subject']}</td><td>{t['message']}</td></tr>"
            for t in all_tickets
        ) or "<tr><td colspan=3 style='color:#888'>No tickets yet</td></tr>"

        admin_link = '<a href="/admin">Admin panel</a> | ' if role == "admin" else ""
        self.send_html(200, f"""<!doctype html>
<html><head><title>TicketDesk</title>
<style>
body{{font-family:sans-serif;max-width:820px;margin:40px auto;padding:0 16px}}
table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:8px;text-align:left}}
input,textarea{{width:100%;margin:4px 0;padding:6px;box-sizing:border-box}}
button{{padding:8px 16px;background:#1a56db;color:#fff;border:none;cursor:pointer}}
.rce{{background:#f0f8ff;border-left:4px solid #1a56db;padding:12px;margin:16px 0}}
pre{{margin:0;white-space:pre-wrap;word-break:break-all}}
a{{color:#1a56db}}
</style></head>
<body>
<h1>TicketDesk</h1>
<p>Logged in as <strong>{username}</strong> ({role}) | {admin_link}<a href="/logout">Log out</a></p>
{rce_block}
<h2>Submit a ticket</h2>
<form method="post" action="/ticket">
<input name="subject" placeholder="Subject">
<textarea name="message" rows="3" placeholder="Describe your issue"></textarea><br>
<button>Submit</button>
</form>
<h2>Your tickets</h2>
<table><tr><th>User</th><th>Subject</th><th>Message</th></tr>
{rows}
</table>
</body></html>""")

    def admin_page(self, flag2: str) -> str:
        return f"""<!doctype html>
<html><head><title>TicketDesk Admin</title>
<style>body{{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 16px}}
a{{color:#1a56db}}.flag{{background:#f0f8ff;border-left:4px solid #1a56db;padding:16px;font-family:monospace}}</style>
</head><body>
<h1>Admin Panel</h1>
<p><a href="/">Back</a></p>
<p>All tickets: {len(TICKETS)}</p>
<div class="flag"><strong>flag2:</strong> {flag2}</div>
</body></html>"""


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
