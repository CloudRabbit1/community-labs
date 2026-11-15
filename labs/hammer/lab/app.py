#!/usr/bin/env python3
"""
Auth bypass via rate-limit evasion + OTP brute force, then command allowlist bypass.

The app exposes a password reset flow protected by a 10-attempts-per-minute
rate limit keyed on the X-Forwarded-For header. Because the rate limiter trusts
that header, an attacker can bypass it by rotating header values.

After resetting the password with a brute-forced OTP, the authenticated
/execute endpoint runs OS commands but only allows id, whoami, and ls.
The check uses startswith(), so "id; cat /flag.txt" passes because it
starts with "id".
"""
import json
import os
import random
import re
import string
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

ALLOWED_CMDS = ["id", "whoami", "ls"]
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 10

_otp_store: dict[str, str] = {}
_sessions: dict[str, str] = {}
_rate: dict[str, list[float]] = {}
REGISTERED_EMAIL = "admin@hammer.local"


def _gen_otp() -> str:
    return f"{random.randint(0, 9999):04d}"


def _gen_token() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=32))


def _check_rate(ip: str) -> bool:
    now = time.time()
    hits = [t for t in _rate.get(ip, []) if now - t < RATE_LIMIT_WINDOW]
    _rate[ip] = hits
    if len(hits) >= RATE_LIMIT_MAX:
        return False
    _rate[ip].append(now)
    return True


def fake_run(cmd: str) -> str:
    if re.search(r'cat\s+/flag', cmd) or '/flag.txt' in cmd:
        return open("/flag.txt").read().strip()
    if cmd.strip().startswith("id"):
        return "uid=1000(app) gid=1000(app) groups=1000(app)"
    if cmd.strip().startswith("whoami"):
        return "app"
    if cmd.strip().startswith("ls"):
        return "app.py"
    return f"sh: {cmd.split()[0]}: command not found"


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

    def _client_ip(self) -> str:
        xff = self.headers.get("X-Forwarded-For", "")
        return xff.split(",")[0].strip() if xff else self.client_address[0]

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_json(200, {
                "service": "Hammer Auth v1.0",
                "endpoints": [
                    "POST /forgot-password   -- request OTP for email",
                    "POST /reset-password    -- submit OTP to get session token",
                    "POST /execute           -- run command (requires Authorization header)",
                ],
            })
            return

        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/forgot-password":
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "invalid JSON"})
                return
            email = data.get("email", "")
            if email != REGISTERED_EMAIL:
                self.send_json(200, {"message": "if that email exists, an OTP has been sent"})
                return
            otp = _gen_otp()
            _otp_store[email] = otp
            self.send_json(200, {"message": "if that email exists, an OTP has been sent"})
            return

        if path == "/reset-password":
            ip = self._client_ip()
            if not _check_rate(ip):
                self.send_json(429, {"error": "too many attempts, slow down"})
                return
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "invalid JSON"})
                return
            email = data.get("email", "")
            otp = data.get("otp", "")
            if email not in _otp_store:
                self.send_json(400, {"error": "no OTP issued for that email"})
                return
            if _otp_store[email] != str(otp):
                self.send_json(401, {"error": "incorrect OTP"})
                return
            token = _gen_token()
            _sessions[token] = email
            del _otp_store[email]
            self.send_json(200, {"token": token})
            return

        if path == "/execute":
            auth = self.headers.get("Authorization", "")
            token = auth.removeprefix("Bearer ").strip()
            if token not in _sessions:
                self.send_json(401, {"error": "unauthorized"})
                return
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "invalid JSON"})
                return
            cmd = data.get("cmd", "")
            if not any(cmd.startswith(a) for a in ALLOWED_CMDS):
                self.send_json(403, {"error": f"command not in allowlist: {ALLOWED_CMDS}"})
                return
            output = fake_run(cmd)
            self.send_json(200, {"cmd": cmd, "output": output})
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    _otp_store[REGISTERED_EMAIL] = _gen_otp()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
