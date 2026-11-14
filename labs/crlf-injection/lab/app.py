"""
CRLF Injection lab.

The /redirect endpoint reads a `url` parameter and passes it directly
to the raw HTTP send_header() call. Python's http.server does NOT
sanitize header values, so injecting %0D%0A (CRLF) splits the header
block and adds attacker-controlled headers.

Flaws:
  1. Header injection: inject any header by splitting the Location value
  2. Cookie injection: inject Set-Cookie to set an arbitrary session cookie

Flags:
  FLAG1: returned from /check-injection when X-Injected header present in request
  FLAG2: returned from /admin when custom_session=admin cookie is present

The /safe-redirect endpoint shows the fix: strip CR and LF before header use.
"""
import json
import os
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FLAG1 = open('/flag1.txt').read().strip()
FLAG2 = open('/flag2.txt').read().strip()


def parse_qs(query: str) -> dict:
    result = {}
    for part in query.split('&'):
        if '=' in part:
            k, v = part.split('=', 1)
            result[urllib.parse.unquote_plus(k)] = urllib.parse.unquote_plus(v)
    return result


class LabHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silence access log

    def send_json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def get_cookies(self) -> dict:
        raw = self.headers.get('Cookie', '')
        cookies = {}
        for part in raw.split(';'):
            part = part.strip()
            if '=' in part:
                k, v = part.split('=', 1)
                cookies[k.strip()] = v.strip()
        return cookies

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query) if parsed.query else {}

        if path == '/':
            self.send_json(200, {
                'app': 'CorpRedirector',
                'endpoints': [
                    'GET /redirect?url=...       -- vulnerable redirect',
                    'GET /safe-redirect?url=...  -- fixed redirect',
                    'GET /check-injection        -- returns flag1 if X-Injected present',
                    'GET /admin                  -- returns flag2 if custom_session=admin',
                    'GET /profile                -- show cookies',
                ],
            })

        elif path == '/redirect':
            url = qs.get('url', '/')
            # VULNERABLE: passes url directly to send_header without sanitizing newlines
            # Injecting \r\n splits the header block
            self.send_response(302)
            self.send_header('Location', url)
            self.end_headers()

        elif path == '/safe-redirect':
            url = qs.get('url', '/')
            # FIXED: strip CR and LF before setting the header
            safe_url = url.replace('\r', '').replace('\n', '')
            self.send_response(302)
            self.send_header('Location', safe_url)
            self.end_headers()

        elif path == '/check-injection':
            # Returns flag1 if the request contains X-Injected header
            injected = self.headers.get('X-Injected', '')
            if injected:
                self.send_json(200, {'flag1': FLAG1, 'injected_value': injected})
            else:
                self.send_json(200, {'message': 'Send X-Injected header to get flag1'})

        elif path == '/admin':
            cookies = self.get_cookies()
            if cookies.get('custom_session') == 'admin':
                self.send_json(200, {'secret': FLAG2})
            else:
                self.send_json(403, {'error': 'Admin only. Set custom_session=admin cookie.'})

        elif path == '/profile':
            cookies = self.get_cookies()
            self.send_json(200, {'cookies': cookies})

        else:
            self.send_json(404, {'error': 'Not found'})


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8080), LabHandler)
    print('Listening on :8080', flush=True)
    server.serve_forever()
