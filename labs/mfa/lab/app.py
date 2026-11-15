#!/usr/bin/env python3
"""
Multi-Factor Authentication bypass via OTP prediction.

The app requires two login steps: a password check followed by a
6-digit OTP. The OTP is derived from the current Unix timestamp
(timestamp mod 1000000), which an attacker can predict by checking
the time before submitting the MFA form.

An attacker who knows the algorithm can skip the guessing entirely:
compute the OTP client-side, complete both steps in a single script,
and obtain the flag without brute force.
"""
import json
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

USERS = {"admin": "password123", "user": "letmein"}

sessions: dict[str, str] = {}


def current_otp() -> str:
    return str(int(time.time()) % 1_000_000).zfill(6)


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

    def body(self) -> dict:
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode(errors="replace") if n else "{}"
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def cookie(self) -> dict:
        raw = self.headers.get("Cookie", "")
        out = {}
        for part in raw.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                out[k.strip()] = v.strip()
        return out

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_json(200, {
                "service": "SecureBank MFA Login v2.0",
                "endpoints": [
                    "POST /login   -- {\"username\": \"...\", \"password\": \"...\"}",
                    "POST /mfa     -- {\"otp\": \"000000\"} (requires pre_auth cookie)",
                    "GET  /flag    -- authenticated session required",
                ],
            })
            return

        if path == "/flag":
            token = self.cookie().get("session", "")
            if token and sessions.get(token) == "authenticated":
                flag = open("/flag.txt").read().strip()
                self.send_json(200, {"flag": flag})
            else:
                self.send_json(401, {"error": "Authentication required"})
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        data = self.body()

        if path == "/login":
            username = data.get("username", "")
            password = data.get("password", "")
            if USERS.get(username) == password:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", f"pre_auth={username}; Path=/")
                body = json.dumps({"status": "password accepted", "next": "POST /mfa with your OTP"}).encode()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_json(401, {"error": "Invalid credentials"})
            return

        if path == "/mfa":
            pre_auth = self.cookie().get("pre_auth", "")
            if not pre_auth:
                self.send_json(401, {"error": "No pre-auth session. Complete /login first."})
                return
            otp = str(data.get("otp", ""))
            expected = current_otp()
            if otp == expected:
                import secrets
                token = secrets.token_hex(16)
                sessions[token] = "authenticated"
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", f"session={token}; Path=/")
                body = json.dumps({"status": "authenticated", "next": "GET /flag"}).encode()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_json(401, {"error": "Invalid OTP"})
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
