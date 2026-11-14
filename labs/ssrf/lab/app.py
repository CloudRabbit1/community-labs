#!/usr/bin/env python3
"""
SSRF lab: the /fetch endpoint makes an HTTP request to a URL supplied by
the user. An internal metadata service on 127.0.0.1:9000 returns the flag.
The endpoint is reachable from the server but not from outside the container.

GET  /             service info
GET  /fetch?url=   fetch a URL and return the response body
"""
import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

FLAG = open("/flag.txt").read().strip()
INTERNAL_PORT = 9000


def start_internal():
    """Metadata service only reachable from localhost."""

    class MetaHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def do_GET(self):
            if self.path == "/secret":
                b = json.dumps({"flag": FLAG}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)
            else:
                self.send_response(404)
                self.end_headers()

    srv = HTTPServer(("127.0.0.1", INTERNAL_PORT), MetaHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()


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

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_json(200, {
                "service": "URL Fetcher v1.0",
                "note": "Fetches URLs on behalf of the user",
                "endpoint": "GET /fetch?url=<url>",
                "example": "GET /fetch?url=http://example.com",
            })
            return

        if path == "/fetch":
            url = params.get("url", [""])[0]
            if not url:
                self.send_json(400, {"error": "url parameter required"})
                return
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "URLFetcher/1.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    body = r.read().decode(errors="replace")
                self.send_json(200, {"url": url, "body": body})
            except urllib.error.URLError as e:
                self.send_json(502, {"error": str(e)})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    start_internal()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
