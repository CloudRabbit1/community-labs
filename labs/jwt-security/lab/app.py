#!/usr/bin/env python3
"""
JWT Security lab: alg:none bypass and weak secret forgery.

POST /login  {"username": "...", "password": "..."} -> JWT token
GET  /admin  Authorization: Bearer <token>          -> flag if username=admin

The server accepts:
  1. HS256 tokens signed with the weak secret "secret123"
  2. Tokens with alg=none and no signature (alg:none bypass)
"""
import base64
import hashlib
import hmac
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = "secret123"
USERS = {"user": "password"}  # admin password is not in here
FLAG = open("/flag.txt").read().strip()


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(s: str) -> bytes:
    pad = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * (pad % 4))


def make_token(username: str) -> str:
    header = b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = b64url_encode(json.dumps({"username": username, "role": "user"}).encode())
    sig_input = f"{header}.{payload}".encode()
    sig = hmac.new(SECRET.encode(), sig_input, hashlib.sha256).digest()
    return f"{header}.{payload}.{b64url_encode(sig)}"


def verify_token(token: str):
    """Return parsed payload dict or raise ValueError."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("malformed token")

    try:
        header = json.loads(b64url_decode(parts[0]))
    except Exception:
        raise ValueError("bad header")

    try:
        payload = json.loads(b64url_decode(parts[1]))
    except Exception:
        raise ValueError("bad payload")

    alg = header.get("alg", "")

    if alg.lower() == "none":
        # alg:none bypass accepted
        return payload

    if alg == "HS256":
        sig_input = f"{parts[0]}.{parts[1]}".encode()
        expected = hmac.new(SECRET.encode(), sig_input, hashlib.sha256).digest()
        try:
            given = b64url_decode(parts[2])
        except Exception:
            raise ValueError("bad signature encoding")
        if not hmac.compare_digest(expected, given):
            raise ValueError("invalid signature")
        return payload

    raise ValueError(f"unsupported algorithm: {alg}")


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

        if path == "/":
            self.send_json(200, {
                "service": "AuthApp v1.0",
                "endpoints": [
                    "POST /login  {\"username\": \"...\", \"password\": \"...\"} -> token",
                    "GET  /admin  Authorization: Bearer <token>          -> flag",
                ],
            })
            return

        if path == "/admin":
            auth = self.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                self.send_json(401, {"error": "Authorization header required"})
                return
            token = auth[len("Bearer "):]
            try:
                payload = verify_token(token)
            except ValueError as e:
                self.send_json(401, {"error": str(e)})
                return
            if payload.get("username") != "admin":
                self.send_json(403, {"error": "admin only"})
                return
            self.send_json(200, {"message": "Welcome, admin.", "flag": FLAG})
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
            if username not in USERS or USERS[username] != password:
                self.send_json(401, {"error": "invalid credentials"})
                return
            token = make_token(username)
            self.send_json(200, {"token": token})
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
