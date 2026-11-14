#!/usr/bin/env python3
"""
Path traversal lab: unsanitized filename parameter lets a student
read arbitrary files, including /flag.txt.

GET /file?name=<filename>   read a file from the document root
GET /                       list available files
"""
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

DOC_ROOT = "/app/docs"
FLAG_PATH = "/flag.txt"


def read_file(name: str):
    # Vulnerable: joins name onto DOC_ROOT without normalizing
    target = os.path.join(DOC_ROOT, name)
    try:
        with open(target, "r", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return None
    except PermissionError:
        return "permission denied"
    except IsADirectoryError:
        return "is a directory"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code: int, data: dict):
        b = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

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
            files = []
            try:
                files = os.listdir(DOC_ROOT)
            except Exception:
                pass
            self.send_json(200, {
                "service": "Document Server v1.0",
                "docs": files,
                "endpoint": "GET /file?name=<filename>",
            })
            return

        if path == "/file":
            name = params.get("name", [""])[0]
            if not name:
                self.send_json(400, {"error": "name parameter required"})
                return
            content = read_file(name)
            if content is None:
                self.send_json(404, {"error": "file not found"})
                return
            self.send_text(200, content)
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
