#!/usr/bin/env python3
"""
SSRF to internal admin panel.

The public app on port 8080 provides a /fetch endpoint that retrieves
any URL and returns the response body. This is meant for previewing
external pages, but nothing restricts it to external addresses.

An internal admin service on 127.0.0.1:9000 returns the flag when
accessed from localhost. From the outside, port 9000 is not exposed.
Only the app itself can reach it.

Sending GET /fetch?url=http://127.0.0.1:9000/admin causes the app to
make the request on behalf of the attacker. Because the request arrives
at the internal service from 127.0.0.1, the admin check passes.
"""
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer


class AdminHandler(BaseHTTPRequestHandler):
    """Internal-only admin service on port 9000."""

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Only accessible from localhost
        client_ip = self.client_address[0]
        if client_ip not in ("127.0.0.1", "::1"):
            body = b"Forbidden: internal service only"
            self.send_response(403)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/admin":
            flag = open("/flag.txt").read().strip().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(flag)))
            self.end_headers()
            self.wfile.write(flag)
            return

        body = b"not found"
        self.send_response(404)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class PublicHandler(BaseHTTPRequestHandler):
    """Public URL preview service on port 8080."""

    def log_message(self, fmt, *args):
        pass

    def send_text(self, code: int, text: str):
        b = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_text(200, (
                "URL Preview Service v1.0\n\n"
                "Endpoints:\n"
                "  GET /fetch?url=<url>  -- fetch a URL and return its content\n"
            ))
            return

        if path == "/fetch":
            url = params.get("url", [""])[0]
            if not url:
                self.send_text(400, "url parameter required")
                return
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "URLPreview/1.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    body = r.read().decode(errors="replace")
                self.send_text(200, body)
            except urllib.error.HTTPError as e:
                self.send_text(e.code, f"HTTP {e.code}: {e.reason}")
            except Exception as exc:
                self.send_text(500, f"error: {exc}")
            return

        self.send_text(404, "not found")


def start_admin():
    HTTPServer(("127.0.0.1", 9000), AdminHandler).serve_forever()


if __name__ == "__main__":
    t = threading.Thread(target=start_admin, daemon=True)
    t.start()
    ThreadingHTTPServer(("0.0.0.0", 8080), PublicHandler).serve_forever()
