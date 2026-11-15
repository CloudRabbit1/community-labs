#!/usr/bin/env python3
"""
Stored XSS via unescaped comment rendering.

A comment board stores user-submitted text in memory and renders it verbatim
in an HTML page. An admin bot visits the page every two seconds. Its session
cookie contains the flag. When a comment contains a script that calls
/steal?c=<cookie>, the bot's visit triggers the simulated theft and the
captured value becomes available at /stolen.
"""
import json
import re
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

FLAG = open("/flag.txt").read().strip()
ADMIN_COOKIE = f"session={FLAG}"

comments = []          # list of raw comment strings
stolen_cookies = []    # captured values from /steal
_lock = threading.Lock()

XSS_PATTERN = re.compile(
    r"""document\.cookie|fetch\s*\(|location\s*=|/steal""",
    re.IGNORECASE,
)


def admin_bot():
    """Simulates an admin user visiting the comment board every 2 seconds."""
    while True:
        time.sleep(2)
        with _lock:
            current = list(comments)
        for comment in current:
            if XSS_PATTERN.search(comment):
                # Admin browser "executes" the script: document.cookie is stolen
                with _lock:
                    stolen_cookies.append(ADMIN_COOKIE)
                break


threading.Thread(target=admin_bot, daemon=True).start()


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head><title>Community Board</title></head>
<body>
<h1>Community Board</h1>
<form method="POST" action="/comment">
  <textarea name="text" rows="3" cols="40" placeholder="Leave a comment..."></textarea><br>
  <button type="submit">Post</button>
</form>
<hr>
<h2>Comments</h2>
{comments_html}
</body>
</html>"""


def render_page():
    with _lock:
        current = list(comments)
    if not current:
        comments_html = "<p>No comments yet.</p>"
    else:
        # Intentionally unescaped: this is the vulnerability
        comments_html = "".join(f"<div class='comment'>{c}</div>" for c in current)
    return HTML_TEMPLATE.format(comments_html=comments_html).encode()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_html(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, code, data):
        b = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode(errors="replace") if n else ""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_html(200, render_page())
            return

        if path == "/steal":
            cookie = params.get("c", [""])[0]
            if cookie:
                with _lock:
                    stolen_cookies.append(cookie)
            self.send_json(200, {"status": "ok"})
            return

        if path == "/stolen":
            with _lock:
                last = stolen_cookies[-1] if stolen_cookies else None
            if last:
                self.send_json(200, {"cookie": last})
            else:
                self.send_json(200, {"cookie": None})
            return

        if path == "/api/comments":
            with _lock:
                current = list(comments)
            self.send_json(200, {"comments": current, "count": len(current)})
            return

        self.send_html(404, b"<h1>Not Found</h1>")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/comment":
            raw = self.body()
            # Accept both form-encoded and JSON
            if self.headers.get("Content-Type", "").startswith("application/x-www-form-urlencoded"):
                text = urllib.parse.parse_qs(raw).get("text", [""])[0]
            elif self.headers.get("Content-Type", "").startswith("application/json"):
                try:
                    text = json.loads(raw).get("text", "")
                except Exception:
                    text = ""
            else:
                text = raw
            if text:
                with _lock:
                    comments.append(text)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
