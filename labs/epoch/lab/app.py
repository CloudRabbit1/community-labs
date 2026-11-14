#!/usr/bin/env python3
"""
Command injection via UNIX timestamp converter.

The /convert endpoint takes a ts parameter and passes it unsanitized into
a shell command string. Shell metacharacters in the input let an attacker
append arbitrary commands after the timestamp value.

This simulates the exact vulnerability in the TryHackMe "Epoch" room:
a timestamp conversion tool that calls date with shell=True.
"""
import os
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

INJECTION_CHARS = re.compile(r'[;|&`$()]')
FLAG_READ = re.compile(r'cat\s+/flag(?:\.txt)?|/flag\.txt')


def convert_timestamp(ts: str) -> dict:
    if INJECTION_CHARS.search(ts):
        base = re.split(r'[;|&`]', ts)[0].strip()
        injected = ts[len(base):].lstrip(';|& \t')
        # Simulate what `date -d @<ts>` would output for the base
        try:
            base_num = int(base) if base else 0
            import datetime
            dt = datetime.datetime.utcfromtimestamp(base_num)
            date_out = dt.strftime("%a %b %d %H:%M:%S UTC %Y")
        except Exception:
            date_out = ""
        if FLAG_READ.search(injected) or 'flag' in injected:
            flag = open("/flag.txt").read().strip()
            return {
                "command": f"date -d @{ts}",
                "output": (date_out + "\n" if date_out else "") + flag,
                "injected": True,
            }
        return {
            "command": f"date -d @{ts}",
            "output": (date_out + "\n" if date_out else "") + f"{injected}: not found",
            "injected": True,
        }
    # Clean input: convert normally
    try:
        ts_int = int(ts)
        import datetime
        dt = datetime.datetime.utcfromtimestamp(ts_int)
        date_out = dt.strftime("%a %b %d %H:%M:%S UTC %Y")
    except Exception:
        return {"error": "invalid timestamp"}
    return {
        "command": f"date -d @{ts}",
        "output": date_out,
        "injected": False,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_text(self, code: int, body: str):
        b = body.encode()
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
                "Epoch Timestamp Converter\n"
                "Usage: GET /convert?ts=<unix_timestamp>\n"
                "Example: GET /convert?ts=0\n"
            ))
            return

        if path == "/convert":
            ts = params.get("ts", [""])[0]
            if not ts:
                self.send_text(400, "ts parameter required\n")
                return
            result = convert_timestamp(ts)
            if "error" in result:
                self.send_text(400, result["error"] + "\n")
                return
            self.send_text(200, result["output"] + "\n")
            return

        self.send_text(404, "Not found\n")


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
