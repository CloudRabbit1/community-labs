#!/usr/bin/env python3
"""
Insecure Direct Object Reference (IDOR).

The document API authenticates requests but does not authorize them. Any
authenticated user can read any document by supplying its integer ID. Document
ownership is never checked. The admin's private document contains the flag.
"""
import json
import os
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS = {
    "alice": {"id": 1, "password": "password123"},
    "admin": {"id": 2, "password": "admin456"},
}

SESSIONS: dict[str, str] = {}


def get_flag() -> str:
    return open("/flag.txt").read().strip()


def build_docs() -> dict[int, dict]:
    return {
        1: {
            "id": 1,
            "owner_id": 1,
            "owner": "alice",
            "title": "Q3 Expense Report",
            "content": "Travel: $420. Meals: $85. Total: $505.",
        },
        2: {
            "id": 2,
            "owner_id": 2,
            "owner": "admin",
            "title": "System Credentials",
            "content": get_flag(),
        },
    }


DOCS = build_docs()


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

    def auth_user(self) -> str | None:
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return SESSIONS.get(auth[7:])
        return None

    def body(self) -> str:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode(errors="replace") if n else ""

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            self.send_json(200, {
                "service": "DocStore API v1",
                "endpoints": [
                    "POST /login",
                    "GET  /api/documents       (your documents)",
                    "GET  /api/documents/<id>  (any document by ID)",
                ],
                "note": "IDOR: document access checks authentication but not ownership",
            })
            return

        if path == "/api/documents":
            user = self.auth_user()
            if not user:
                self.send_json(401, {"error": "Authorization required"})
                return
            uid = USERS[user]["id"]
            owned = [d for d in DOCS.values() if d["owner_id"] == uid]
            self.send_json(200, {"documents": owned, "note": "Your documents only"})
            return

        if path.startswith("/api/documents/"):
            user = self.auth_user()
            if not user:
                self.send_json(401, {"error": "Authorization required"})
                return
            try:
                doc_id = int(path.split("/")[-1])
            except ValueError:
                self.send_json(400, {"error": "Invalid document ID"})
                return
            doc = DOCS.get(doc_id)
            if not doc:
                self.send_json(404, {"error": "Document not found"})
                return
            # Bug: returns any document to any authenticated user, no ownership check
            self.send_json(200, {"document": doc})
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
            uname = data.get("username", "")
            pw = data.get("password", "")
            user = USERS.get(uname)
            if user and user["password"] == pw:
                token = secrets.token_hex(16)
                SESSIONS[token] = uname
                self.send_json(200, {"token": token, "user": uname})
            else:
                self.send_json(401, {"error": "Invalid credentials"})
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
