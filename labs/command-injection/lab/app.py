#!/usr/bin/env python3
"""
OS Command Injection via unsanitized shell input.

A network diagnostic tool passes the user-supplied host parameter directly
into a shell command string. Any shell metacharacter (;, |, &&, backtick,
$()) in the input lets an attacker append arbitrary commands.

This simulation detects injection patterns and returns the flag when the
injected command reads /flag.txt.
"""
import json
import os
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

INJECTION_CHARS = re.compile(r'[;|&`$()]')
FLAG_READ = re.compile(r'cat\s*(?:\$\{IFS\}|/|\s+/).*flag|/flag\.txt')


def fake_ping(host: str) -> str:
    return (
        f"PING {host} ({host}): 56 data bytes\n"
        f"64 bytes from {host}: icmp_seq=0 ttl=64 time=0.412 ms\n"
        f"64 bytes from {host}: icmp_seq=1 ttl=64 time=0.391 ms\n"
        f"64 bytes from {host}: icmp_seq=2 ttl=64 time=0.403 ms\n"
        f"--- {host} ping statistics ---\n"
        f"3 packets transmitted, 3 received, 0% packet loss"
    )


def run_ping(host: str) -> dict:
    if INJECTION_CHARS.search(host):
        # Injection detected: split on the first metachar, run the injected command
        base = re.split(r'[;|&`]', host)[0].strip()
        injected = host[len(base):].lstrip(';|& \t')
        ping_out = fake_ping(base) if base else ""
        if FLAG_READ.search(injected) or 'flag' in injected:
            flag = open("/flag.txt").read().strip()
            return {
                "command": f"ping -c 3 {host}",
                "output": ping_out + ("\n" if ping_out else "") + flag,
                "injected": True,
            }
        # Injection present but not reading the flag
        return {
            "command": f"ping -c 3 {host}",
            "output": ping_out + f"\n{injected}: command output (not shown)",
            "injected": True,
        }
    return {
        "command": f"ping -c 3 {host}",
        "output": fake_ping(host),
        "injected": False,
    }


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

    def body(self) -> str:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode(errors="replace") if n else ""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_json(200, {
                "service": "Network Diagnostics v1.0",
                "endpoints": [
                    "GET  /ping?host=<host>  -- ping a host",
                    "POST /ping              -- ping via JSON body {\"host\": \"...\"}",
                ],
            })
            return

        if path == "/ping":
            host = params.get("host", [""])[0]
            if not host:
                self.send_json(400, {"error": "host parameter required"})
                return
            self.send_json(200, run_ping(host))
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/ping":
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "Invalid JSON"})
                return
            host = data.get("host", "")
            if not host:
                self.send_json(400, {"error": "host field required"})
                return
            self.send_json(200, run_ping(host))
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
