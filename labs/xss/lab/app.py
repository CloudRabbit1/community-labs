#!/usr/bin/env python3
"""
XSS lab: three attack vectors in one app.

1. Reflected XSS   GET /search?q=<input>  -- input echoed raw into HTML
2. Stored XSS      POST /comment          -- comment stored and rendered unsanitized
3. DOM XSS         GET /                  -- JS reads location.hash and writes innerHTML

The flag is stored in the admin session cookie. The XSS payloads demonstrate
how JavaScript can exfiltrate data from the page or other users' sessions.

For this lab, the flag is returned directly when the payload contains the
string 'document.cookie' or 'document.location' (simulating cookie theft).
"""
import html as html_mod
import json
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

COMMENTS: list = []
FLAG = open("/flag.txt").read().strip()
ADMIN_COOKIE = f"admin_session={FLAG}"


def has_xss_trigger(text: str) -> bool:
    """Return True if the payload simulates cookie exfiltration."""
    lowered = text.lower()
    return "document.cookie" in lowered or "document.location" in lowered


def render_page(title: str, body_html: str) -> bytes:
    return f"""<!DOCTYPE html>
<html>
<head><title>{title}</title></head>
<body>
<h1>{title}</h1>
<p><a href="/">Home</a> | <a href="/search">Search</a> | <a href="/comment">Comments</a></p>
{body_html}
</body>
</html>""".encode()


def home_page() -> bytes:
    return render_page("Home", """
<p>Welcome. This site has a search box and a comment board.</p>
<p>XSS hint: the <code>hash</code> fragment of this URL is written to the page via <code>innerHTML</code>.</p>
<div id="message"></div>
<script>
  var hash = decodeURIComponent(location.hash.slice(1));
  if (hash) document.getElementById('message').innerHTML = hash;
</script>
""")


def search_page(q: str) -> bytes:
    if has_xss_trigger(q):
        return render_page("Search", f"""
<p>Results for: {q}</p>
<p>Admin cookie captured: <code>{ADMIN_COOKIE}</code></p>
<p><strong>Flag: {FLAG}</strong></p>
""").replace(b"Flag:", b"Flag (simulated cookie theft):")
    # Reflect raw, unsanitized input
    return render_page("Search", f"<p>Results for: {q}</p><p>No results found.</p>")


def comments_page(message: str = "") -> bytes:
    comment_html = ""
    for c in COMMENTS:
        # Stored XSS: comments are rendered without escaping
        comment_html += f"<div class='comment'>{c}</div>\n"
        if has_xss_trigger(c):
            comment_html += f"<p>Admin cookie: <code>{ADMIN_COOKIE}</code></p><p><strong>Flag: {FLAG}</strong></p>\n"
    return render_page("Comments", f"""
{message}
<form method='POST' action='/comment'>
<textarea name='comment' rows='3' cols='40'></textarea>
<br><input type='submit' value='Post'>
</form>
<h2>Comments:</h2>
{comment_html}
""")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_html(self, code: int, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, code: int, data: dict):
        b = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body_str(self) -> str:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode(errors="replace") if n else ""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_html(200, home_page())
            return

        if path == "/search":
            q = params.get("q", [""])[0]
            if not q:
                self.send_html(200, render_page("Search", '<form><input name="q" /><input type="submit" value="Search"></form>'))
                return
            self.send_html(200, search_page(q))
            return

        if path == "/comment":
            self.send_html(200, comments_page())
            return

        if path == "/flag":
            # API endpoint: returns flag only if the cookie header contains the admin session
            cookie = self.headers.get("Cookie", "")
            if f"admin_session={FLAG}" in cookie:
                self.send_json(200, {"flag": FLAG})
            else:
                self.send_json(403, {"error": "admin session required"})
            return

        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/comment":
            body = self.body_str()
            data = urllib.parse.parse_qs(body)
            comment = data.get("comment", [""])[0]
            if comment:
                COMMENTS.append(comment)
            self.send_response(302)
            self.send_header("Location", "/comment")
            self.end_headers()
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
