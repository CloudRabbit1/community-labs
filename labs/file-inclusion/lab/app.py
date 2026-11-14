#!/usr/bin/env python3
"""
Local File Inclusion via unsanitized path parameter.

The app reads files from a pages/ directory using a user-supplied filename.
No path sanitization means traversal sequences (../../) escape the directory.
"""
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

PAGES_DIR = "/app/pages"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_text(self, code: int, body: str, content_type: str = "text/plain"):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        path = parsed.path

        if path == "/" and "page" not in params:
            self.send_text(200, (
                "Welcome to the site.\n\n"
                "Available pages: about, contact\n"
                "Usage: GET /?page=about.txt\n"
            ))
            return

        if path == "/" and "page" in params:
            page = params["page"][0]
            # Vulnerable: joins page directly with PAGES_DIR, no sanitization
            full_path = os.path.join(PAGES_DIR, page)
            try:
                with open(full_path) as f:
                    content = f.read()
                self.send_text(200, content)
            except FileNotFoundError:
                self.send_text(404, f"Page not found: {page}\n")
            except PermissionError:
                self.send_text(403, "Permission denied.\n")
            except Exception as e:
                self.send_text(500, f"Error: {e}\n")
            return

        self.send_text(404, "Not found.\n")


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
