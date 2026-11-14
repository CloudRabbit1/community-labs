#!/usr/bin/env python3
"""
CVE-2023-4911 — Looney Tunables (glibc GLIBC_TUNABLES heap buffer overflow).

The glibc dynamic loader (ld.so) parses the GLIBC_TUNABLES environment variable
at process startup. In glibc 2.34 through 2.38, the parsing routine copies the
variable's value into a fixed-size heap buffer without bounds checking. A specially
crafted value that starts with "glibc.malloc.mxfast=" and exceeds the buffer size
triggers a heap overflow, corrupting adjacent metadata and enabling local privilege
escalation to root.

Disclosed by Qualys, October 2023. CVSS 7.8. Fixed in glibc 2.39.

This simulation models the vulnerable parsing logic: the helper process that
processes GLIBC_TUNABLES values accepts any string, but overlong values starting
with the vulnerable key name corrupt the privilege check.
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# The heap buffer in glibc's _dl_process_pt_gnu_property is 256 bytes.
# Values longer than this overflow it.
BUFFER_SIZE = 256
OVERFLOW_KEY = "glibc.malloc.mxfast="


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code, data):
        b = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(b))
        self.end_headers()
        self.wfile.write(b)

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode(errors="replace") if n else ""

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            self.send_json(200, {
                "service": "glibc-tunable-helper v2.38",
                "description": "SUID helper that processes GLIBC_TUNABLES for privilege tasks",
                "endpoints": [
                    "GET  /info",
                    "POST /run-helper",
                ],
            })
            return

        if path == "/info":
            self.send_json(200, {
                "glibc_version": "2.38",
                "buffer_size": BUFFER_SIZE,
                "overflow_trigger": f"value starting with '{OVERFLOW_KEY}' longer than {BUFFER_SIZE} bytes",
                "note": "CVE-2023-4911: GLIBC_TUNABLES heap buffer overflow",
            })
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/run-helper":
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "Invalid JSON"})
                return

            tunables = data.get("glibc_tunables", "")

            # Simulate the vulnerable parsing:
            # The overflow is triggered when the value starts with the vulnerable
            # key name and the total length exceeds the fixed heap buffer.
            if tunables.startswith(OVERFLOW_KEY) and len(tunables) > BUFFER_SIZE:
                # Heap overflow corrupts the privilege check — process runs as root
                flag = open("/flag.txt").read().strip()
                self.send_json(200, {
                    "exit_code": 0,
                    "privilege": "root",
                    "output": f"uid=0(root) gid=0(root) groups=0(root)",
                    "flag": flag,
                    "note": "Heap overflow triggered — privilege escalation succeeded",
                })
                return

            # Normal execution — no overflow
            self.send_json(200, {
                "exit_code": 0,
                "privilege": "user",
                "output": "uid=1000(user) gid=1000(user)",
                "note": "No overflow — running as unprivileged user",
            })
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
