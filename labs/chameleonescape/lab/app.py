#!/usr/bin/env python3
"""
ChameleonEscape — container escape via SYS_PTRACE capability.

The container runs with CAP_SYS_PTRACE, which lets any process inside the
container attach to any process on the host, including PID 1 (init/systemd).
Attachment via /proc/<pid>/mem lets an attacker read and write arbitrary host
process memory without a kernel CVE — just a misconfigured container.

The container appears harmless: it exposes a "process debugger" API for
performance monitoring. The vulnerability is in what CAP_SYS_PTRACE allows.
"""
import json
import os
import re
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Capabilities this container was started with (the misconfiguration)
CAPABILITIES = {
    "CapEff": "0000000000400000",  # CAP_SYS_PTRACE only
    "decoded": ["CAP_SYS_PTRACE"],
    "note": "Container was launched with SYS_PTRACE; intended for perf monitoring",
}

# Simulated process table — PID 1 is the HOST init process, visible from
# inside the container because we share the host PID namespace (--pid=host).
PROCESSES = [
    {"pid": 1,    "name": "systemd",    "user": "root", "cmdline": "/sbin/init", "host": True},
    {"pid": 7,    "name": "sshd",       "user": "root", "cmdline": "/usr/sbin/sshd -D", "host": True},
    {"pid": 843,  "name": "dockerd",    "user": "root", "cmdline": "/usr/bin/dockerd", "host": True},
    {"pid": 1024, "name": "containerd", "user": "root", "cmdline": "/usr/bin/containerd", "host": True},
    {"pid": 2047, "name": "python3",    "user": "app",  "cmdline": "python3 /app/app.py", "host": False},
]

# Simulated /proc/<pid>/maps for PID 1 — the host init process
PROC1_MAPS = [
    {"start": "0x55a000000000", "end": "0x55a000800000", "perms": "r-xp", "label": "[systemd .text]"},
    {"start": "0x55a000a00000", "end": "0x55a000c00000", "perms": "r--p", "label": "[systemd .rodata]"},
    {"start": "0x7f4000000000", "end": "0x7f4000400000", "perms": "r--p", "label": "[heap]"},
    {"start": "0x7f4000400000", "end": "0x7f4000500000", "perms": "rw-p", "label": "[runtime state]"},
    {"start": "0x7f4000500000", "end": "0x7f4000501000", "perms": "r--p", "label": "[mmap anon]"},
    {"start": "0x7fff00000000", "end": "0x7fff00010000", "perms": "rw-p", "label": "[stack]"},
]

# Memory contents at the flag segment (0x7f4000500000)
FLAG_ADDR = "0x7f4000500000"


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

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        path = parsed.path

        if path == "/":
            self.send_json(200, {
                "service": "ChameleonDebugger v1.4",
                "description": "In-container process performance monitor",
                "endpoints": [
                    "GET  /api/caps",
                    "GET  /api/processes",
                    "GET  /api/process/<pid>/maps",
                    "GET  /api/process/<pid>/mem?addr=<hex>&size=<n>",
                ],
            })
            return

        if path == "/api/caps":
            self.send_json(200, CAPABILITIES)
            return

        if path == "/api/processes":
            self.send_json(200, {"processes": PROCESSES})
            return

        # /api/process/<pid>/maps
        m = re.match(r"^/api/process/(\d+)/maps$", path)
        if m:
            pid = int(m.group(1))
            if pid == 1:
                self.send_json(200, {"pid": 1, "maps": PROC1_MAPS})
            elif any(p["pid"] == pid for p in PROCESSES):
                self.send_json(200, {"pid": pid, "maps": [
                    {"start": "0x400000", "end": "0x401000", "perms": "r-xp", "label": "[.text]"},
                    {"start": "0x7fff00000000", "end": "0x7fff00010000", "perms": "rw-p", "label": "[stack]"},
                ]})
            else:
                self.send_json(404, {"error": f"No process with pid {pid}"})
            return

        # /api/process/<pid>/mem?addr=<hex>&size=<n>
        m = re.match(r"^/api/process/(\d+)/mem$", path)
        if m:
            pid = int(m.group(1))
            addr = params.get("addr", "")
            size = int(params.get("size", "64"))

            # Only host processes are reachable via ptrace
            proc = next((p for p in PROCESSES if p["pid"] == pid), None)
            if not proc:
                self.send_json(404, {"error": f"No process with pid {pid}"})
                return

            if not proc["host"]:
                self.send_json(403, {
                    "error": "Cannot ptrace container process from within same container",
                })
                return

            # Simulate ptrace read: flag lives in PID 1's anonymous mmap segment
            if pid == 1 and addr == FLAG_ADDR:
                flag = open("/flag.txt").read().strip()
                self.send_json(200, {
                    "pid": 1,
                    "addr": addr,
                    "size": size,
                    "data": flag,
                    "note": "Host process memory read via CAP_SYS_PTRACE + /proc/1/mem",
                })
                return

            # Other readable addresses return dummy data
            self.send_json(200, {
                "pid": pid,
                "addr": addr,
                "size": size,
                "data": "00 00 00 00 00 00 00 00" * (size // 8),
            })
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
