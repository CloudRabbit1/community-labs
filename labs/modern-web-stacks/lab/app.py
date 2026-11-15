#!/usr/bin/env python3
"""
Next.js-style middleware bypass.

A middleware layer inspects the x-middleware-subrequest header to determine
whether a request was already processed by the middleware chain. If the header
is present and set to "middleware", the middleware trusts it and skips the auth
check. An attacker can forge this header to reach protected routes without a
valid session.

This simulates CVE-2025-29927, a real vulnerability in Next.js that allowed
unauthenticated access to any route protected by middleware.
"""
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

ADMIN_COOKIE = "session=valid-admin-token"
MIDDLEWARE_HEADER = "x-middleware-subrequest"
MIDDLEWARE_TRUST_VALUE = "middleware"


def is_authenticated(headers) -> bool:
    cookie = headers.get("Cookie", "")
    return ADMIN_COOKIE in cookie


def middleware_bypassed(headers) -> bool:
    val = headers.get(MIDDLEWARE_HEADER, "")
    return val == MIDDLEWARE_TRUST_VALUE


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_html(self, code: int, body: str):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_html(200, (
                "<html><body>"
                "<h1>NextApp</h1>"
                "<p>Welcome to the demo application.</p>"
                "<p><a href='/admin'>Admin Panel</a></p>"
                "</body></html>"
            ))
            return

        if path == "/admin":
            if is_authenticated(self.headers) or middleware_bypassed(self.headers):
                flag = open("/flag.txt").read().strip()
                self.send_html(200, (
                    "<html><body>"
                    "<h1>Admin Panel</h1>"
                    f"<p>Flag: <code>{flag}</code></p>"
                    "</body></html>"
                ))
            else:
                self.send_html(401, (
                    "<html><body>"
                    "<h1>401 Unauthorized</h1>"
                    "<p>Valid session required.</p>"
                    "</body></html>"
                ))
            return

        self.send_html(404, "<html><body><h1>404 Not Found</h1></body></html>")


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
