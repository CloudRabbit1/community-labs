#!/usr/bin/env python3
"""
CVE-2025-25227 — Joomla MFA authentication bypass.

After a successful login, Joomla sets state=logged_in but requires MFA
verification before granting access to admin routes. The bug: admin route
handlers check state == "logged_in" but not mfa_verified == True. An
attacker skips the MFA step entirely, jumping straight from login to admin.
"""
import hashlib
import json
import os
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS = {
    "admin": {"password": "joom1aAdmin!", "role": "admin"},
    "editor": {"password": "editor123", "role": "editor"},
}

# token -> {username, role, state, mfa_verified}
SESSIONS: dict = {}

MFA_CODE = "123456"  # simulated TOTP


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

    def session_from_headers(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return SESSIONS.get(auth[7:])
        return None

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            self.send_json(200, {
                "cms": "Joomla! 5.2.5",
                "endpoints": [
                    "POST /api/v1/login",
                    "GET  /api/v1/mfa-challenge",
                    "POST /api/v1/mfa-verify",
                    "GET  /administrator/flag",
                ],
            })
            return

        if path == "/api/v1/mfa-challenge":
            session = self.session_from_headers()
            if not session:
                self.send_json(401, {"error": "Not authenticated"})
                return
            self.send_json(200, {
                "type": "totp",
                "digits": 6,
                "note": "Enter the 6-digit code from your authenticator app",
            })
            return

        # Admin route — vulnerable: checks state but NOT mfa_verified
        if path == "/administrator/flag":
            session = self.session_from_headers()
            if not session:
                self.send_json(401, {"error": "Not authenticated"})
                return
            if session.get("state") != "logged_in":
                self.send_json(403, {"error": "Login required"})
                return
            # BUG: should also check session.get("mfa_verified") == True
            flag = open("/flag.txt").read().strip()
            self.send_json(200, {
                "flag": flag,
                "note": "MFA step was skipped — CVE-2025-25227",
            })
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/api/v1/login":
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "Invalid JSON"})
                return
            username = data.get("username", "")
            password = data.get("password", "")
            user = USERS.get(username)
            if not user or user["password"] != password:
                self.send_json(401, {"error": "Invalid credentials"})
                return
            token = secrets.token_hex(32)
            SESSIONS[token] = {
                "username": username,
                "role": user["role"],
                "state": "logged_in",
                "mfa_verified": False,
            }
            self.send_json(200, {
                "token": token,
                "mfa_required": True,
                "next_step": "/api/v1/mfa-challenge",
            })
            return

        if path == "/api/v1/mfa-verify":
            session = self.session_from_headers()
            if not session:
                self.send_json(401, {"error": "Not authenticated"})
                return
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "Invalid JSON"})
                return
            code = data.get("code", "")
            if code != MFA_CODE:
                self.send_json(401, {"error": "Invalid MFA code"})
                return
            session["mfa_verified"] = True
            self.send_json(200, {"message": "MFA verified", "mfa_verified": True})
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
