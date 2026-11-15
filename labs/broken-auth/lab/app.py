#!/usr/bin/env python3
"""
Broken Authentication lab: a login form is vulnerable to two auth flaws:
1. Username enumeration via different error messages (OWASP A07)
2. The admin account has a weak password in a short wordlist

GET  /           service info
POST /login      {"username": "...", "password": "..."} -> session cookie
GET  /dashboard  requires valid session for 'admin'

Weak passwords used: admin:admin123, user:password
"""
import hashlib
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

# Vulnerable: different messages for unknown user vs wrong password
USERS = {
    "user": "password",
    "admin": "admin123",
}
SESSIONS: dict = {}
FLAG = open("/flag.txt").read().strip()


def make_session(username: str) -> str:
    token = hashlib.sha256(os.urandom(16)).hexdigest()
    SESSIONS[token] = username
    return token


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code: int, data: dict, headers: dict = None):
        b = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def body(self) -> str:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode(errors="replace") if n else ""

    def session_user(self) -> str:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith("session="):
                token = part[len("session="):]
                return SESSIONS.get(token, "")
        return ""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_json(200, {
                "service": "Portal v1.0",
                "endpoints": [
                    "POST /login      {\"username\": \"...\", \"password\": \"...\"}",
                    "GET  /dashboard  (requires admin session)",
                ],
            })
            return

        if path == "/dashboard":
            user = self.session_user()
            if not user:
                self.send_json(401, {"error": "login required"})
                return
            if user != "admin":
                self.send_json(403, {"error": "admin only"})
                return
            self.send_json(200, {"message": f"Welcome, {user}.", "flag": FLAG})
            return

        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/login":
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "invalid JSON"})
                return

            username = data.get("username", "")
            password = data.get("password", "")

            if username not in USERS:
                # Vulnerable: reveals that the username does not exist
                self.send_json(401, {"error": "user not found"})
                return

            if USERS[username] != password:
                # Vulnerable: different message confirms the user exists
                self.send_json(401, {"error": "incorrect password"})
                return

            token = make_session(username)
            self.send_json(200,
                {"message": f"logged in as {username}"},
                headers={"Set-Cookie": f"session={token}; HttpOnly; Path=/"},
            )
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
