#!/usr/bin/env python3
"""
CORS misconfiguration: origin reflection with credentials.

The server reflects any Origin header value back in Access-Control-Allow-Origin
and sets Access-Control-Allow-Credentials: true. A page on any origin can make
credentialed cross-origin requests and read the response, leaking session data.

The fix is to validate the Origin against an explicit allowlist before reflecting
it. Wildcard (*) cannot be used with Allow-Credentials: true per the CORS spec.
"""
import json
import os
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS = {"alice": "password123", "bob": "hunter2"}
SESSIONS: dict[str, str] = {}


def get_flag() -> str:
    return open("/flag.txt").read().strip()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code: int, data: dict, extra_headers: dict | None = None):
        b = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def cors_headers(self) -> dict:
        origin = self.headers.get("Origin", "")
        headers = {}
        if origin:
            # Bug: reflecting any origin instead of checking against an allowlist
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
            headers["Vary"] = "Origin"
        return headers

    def session_user(self) -> str | None:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            k, _, v = part.strip().partition("=")
            if k.strip() == "session":
                return SESSIONS.get(v.strip())
        return None

    def body(self) -> str:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode(errors="replace") if n else ""

    def do_OPTIONS(self):
        path = self.path.split("?")[0]
        if path == "/api/profile":
            hdrs = self.cors_headers()
            hdrs["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            hdrs["Access-Control-Allow-Headers"] = "Content-Type"
            self.send_response(204)
            for k, v in hdrs.items():
                self.send_header(k, v)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            self.send_json(200, {
                "service": "ProfileAPI v2",
                "endpoints": [
                    "POST /login",
                    "GET  /api/profile  (session cookie required)",
                ],
                "note": "CORS misconfiguration: Origin header is reflected without validation",
            })
            return

        if path == "/api/profile":
            user = self.session_user()
            if not user:
                self.send_json(401, {"error": "Not authenticated"}, self.cors_headers())
                return
            self.send_json(200, {
                "username": user,
                "email": f"{user}@corp.internal",
                "role": "user",
                "flag": get_flag(),
            }, self.cors_headers())
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/login":
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "Invalid JSON"})
                return
            user = data.get("username", "")
            pw = data.get("password", "")
            if USERS.get(user) == pw:
                token = secrets.token_hex(16)
                SESSIONS[token] = user
                b = json.dumps({"status": "logged in", "user": user}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(b)))
                self.send_header("Set-Cookie", f"session={token}; Path=/; HttpOnly")
                self.end_headers()
                self.wfile.write(b)
            else:
                self.send_json(401, {"error": "Invalid credentials"})
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
