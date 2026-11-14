#!/usr/bin/env python3
"""
LDAP Injection via unsanitized filter string.

A login form builds an LDAP search filter by directly interpolating the
username and password into the filter string. Special LDAP metacharacters
in the input modify the filter logic, bypassing authentication.

This simulation parses the constructed filter string to detect injection
rather than running a real LDAP server.
"""
import json
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

# Simulated LDAP directory: one admin user.
USERS = {
    "admin": {"password": "xT8!mK#2pQv9", "cn": "Admin User", "role": "admin"},
}


def build_filter(username: str, password: str) -> str:
    return f"(&(uid={username})(userPassword={password}))"


def ldap_query(ldap_filter: str) -> dict | None:
    """
    Simulate LDAP query by parsing the filter string.

    A correctly formed filter with matching uid+password returns the user.
    An injected filter that short-circuits the uid check without a valid
    password is detected via the injection pattern.
    """
    # Detect the classic LDAP injection bypass pattern:
    # injected uid=* wildcard with OR clause short-circuits password check.
    injection_pattern = re.compile(r'\)\(uid=\*\)\)\(\|')
    if injection_pattern.search(ldap_filter):
        # Injection detected: attacker bypassed auth, return admin user.
        return USERS["admin"]

    # Normal path: extract uid and userPassword from a well-formed filter.
    uid_match = re.search(r'\(uid=([^)]+)\)', ldap_filter)
    pwd_match = re.search(r'\(userPassword=([^)]+)\)', ldap_filter)
    if uid_match and pwd_match:
        uid = uid_match.group(1)
        pwd = pwd_match.group(1)
        user = USERS.get(uid)
        if user and user["password"] == pwd:
            return user
    return None


def do_login(username: str, password: str) -> dict:
    ldap_filter = build_filter(username, password)
    result = ldap_query(ldap_filter)
    if result:
        flag = open("/flag.txt").read().strip()
        return {
            "success": True,
            "user": result["cn"],
            "role": result["role"],
            "filter_used": ldap_filter,
            "flag": flag,
        }
    return {
        "success": False,
        "error": "Invalid credentials",
        "filter_used": ldap_filter,
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
        if self.path == "/":
            self.send_json(200, {
                "service": "Directory Services Portal v1.3",
                "endpoints": [
                    "POST /login  -- body: username=<u>&password=<p>",
                ],
                "note": "Authentication backed by LDAP directory.",
            })
            return
        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/login":
            raw = self.body()
            params = urllib.parse.parse_qs(raw)
            username = params.get("username", [""])[0]
            password = params.get("password", [""])[0]
            if not username:
                self.send_json(400, {"error": "username required"})
                return
            self.send_json(200, do_login(username, password))
            return
        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
