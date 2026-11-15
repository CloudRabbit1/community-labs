#!/usr/bin/env python3
"""
Session prediction via sequential session token IDs.

The app assigns session tokens as session_1, session_2, session_3, ...
Admin registers first at startup and receives session_1. Any user who
registers later can observe their own token (e.g. session_5) and work
backwards to guess the admin token (session_1).

Sending GET /admin with Cookie: session=session_1 returns the flag.
"""
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

_lock = threading.Lock()
_counter = 0
_sessions: dict[str, str] = {}
_users: dict[str, str] = {}


def _next_token() -> str:
    global _counter
    with _lock:
        _counter += 1
        return f"session_{_counter}"


def _bootstrap():
    token = _next_token()
    _sessions[token] = "admin"
    _users["admin"] = "admin_secret"


_bootstrap()


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
        out: dict[str, str] = {}
        for part in raw.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                out[k.strip()] = v.strip()
        return out

    def session_user(self) -> str:
        token = self.cookie().get("session", "")
        return _sessions.get(token, "")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_json(200, {
                "service": "NoteKeeper v1.0",
                "endpoints": [
                    "POST /register  -- {\"username\": \"...\", \"password\": \"...\"}",
                    "POST /login     -- {\"username\": \"...\", \"password\": \"...\"}",
                    "GET  /profile   -- returns your username (session required)",
                    "GET  /admin     -- admin only",
                ],
            })
            return

        if path == "/profile":
            user = self.session_user()
            if not user:
                self.send_json(401, {"error": "No valid session"})
            else:
                self.send_json(200, {"username": user})
            return

        if path == "/admin":
            user = self.session_user()
            if user == "admin":
                flag = open("/flag.txt").read().strip()
                self.send_json(200, {"message": "Welcome, admin.", "flag": flag})
            elif user:
                self.send_json(403, {"error": "Admin only"})
            else:
                self.send_json(401, {"error": "No valid session"})
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        data = self.body()

        if path == "/register":
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
            if not username or not password:
                self.send_json(400, {"error": "username and password required"})
                return
            if username in _users:
                self.send_json(409, {"error": "Username taken"})
                return
            _users[username] = password
            token = _next_token()
            _sessions[token] = username
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie", f"session={token}; Path=/")
            body = json.dumps({"status": "registered", "username": username}).encode()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/login":
            username = data.get("username", "")
            password = data.get("password", "")
            if _users.get(username) == password:
                token = _next_token()
                _sessions[token] = username
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", f"session={token}; Path=/")
                body = json.dumps({"status": "logged in"}).encode()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_json(401, {"error": "Invalid credentials"})
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
