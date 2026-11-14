#!/usr/bin/env python3
"""
ORM Injection via raw SQL string interpolation.

A login form passes username and password directly into a SQL query string
using Python string formatting. No parameterized queries, no escaping.
Injecting a SQL comment into the username closes the WHERE clause early
and bypasses the password check entirely.
"""
import json
import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

# In-memory database seeded with one admin user.
# The password is intentionally long and unguessable.
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)"
)
DB.execute(
    "INSERT INTO users VALUES (1, 'admin', 'x9kQ2!mPvL#8nRw', 'admin')"
)
DB.commit()


def do_login(username: str, password: str) -> dict:
    # Vulnerable query: string interpolation instead of parameterized query.
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    try:
        row = DB.execute(query).fetchone()
    except sqlite3.OperationalError as e:
        return {"success": False, "error": str(e)}

    if row:
        flag = open("/flag.txt").read().strip()
        return {"success": True, "user": row[1], "role": row[3], "flag": flag}
    return {"success": False, "error": "Invalid credentials"}


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
                "service": "Employee Portal v2.1",
                "endpoints": [
                    "POST /login  -- body: username=<u>&password=<p>",
                ],
                "hint": "Login is for authorized employees only.",
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
