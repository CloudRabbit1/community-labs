#!/usr/bin/env python3
"""
OAuth 2.0 open redirect via unvalidated redirect_uri.

The authorization server accepts any redirect_uri without checking it
against the client's pre-registered URIs. An attacker who controls the
redirect destination receives the authorization code and can exchange it
for a token granting access to the victim's account.
"""
import json
import secrets
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

# Registered OAuth clients with their allowed redirect URIs
CLIENTS = {
    "app": {
        "secret": "client_secret_app",
        "registered_uris": ["http://localhost:8080/callback"],
        "name": "Lab Application",
    }
}

# In-memory state
PENDING_CODES = {}   # code -> {client_id, redirect_uri, user}
ACCESS_TOKENS = {}   # token -> {user}
USERS = {
    "alice": {"name": "Alice", "email": "alice@example.com"},
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

    def read_body(self) -> bytes:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_json(200, {
                "service": "OAuth 2.0 Authorization Server",
                "endpoints": [
                    "GET  /oauth/authorize?client_id=app&redirect_uri=<uri>&state=<state>",
                    "POST /oauth/authorize  {client_id, redirect_uri, state, allow: true}",
                    "POST /oauth/token      {grant_type, code, redirect_uri, client_id, client_secret}",
                    "GET  /api/me           Authorization: Bearer <token>",
                ],
            })
            return

        if path == "/oauth/authorize":
            client_id = params.get("client_id", [""])[0]
            redirect_uri = params.get("redirect_uri", [""])[0]
            state = params.get("state", [""])[0]

            if client_id not in CLIENTS:
                self.send_json(400, {"error": "unknown_client"})
                return

            # BUG: redirect_uri is accepted without validating against registered_uris
            self.send_json(200, {
                "message": "POST to /oauth/authorize with allow=true to approve",
                "client": CLIENTS[client_id]["name"],
                "redirect_uri": redirect_uri,
                "state": state,
                "scope": "read",
            })
            return

        if path == "/api/me":
            auth = self.headers.get("Authorization", "")
            token = auth.removeprefix("Bearer ").strip()
            user_data = ACCESS_TOKENS.get(token)
            if not user_data:
                self.send_json(401, {"error": "invalid_token"})
                return
            user = user_data["user"]
            info = USERS.get(user, {})
            flag = open("/flag.txt").read().strip()
            self.send_json(200, {
                "user": user,
                "email": info.get("email"),
                "flag": flag,
            })
            return

        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            data = json.loads(self.read_body())
        except Exception:
            self.send_json(400, {"error": "invalid_json"})
            return

        if path == "/oauth/authorize":
            client_id = data.get("client_id", "")
            redirect_uri = data.get("redirect_uri", "")
            state = data.get("state", "")
            allow = data.get("allow", False)

            if client_id not in CLIENTS:
                self.send_json(400, {"error": "unknown_client"})
                return
            if not allow:
                self.send_json(400, {"error": "access_denied"})
                return

            # BUG: redirect_uri is not validated against CLIENTS[client_id]["registered_uris"]
            code = secrets.token_hex(16)
            PENDING_CODES[code] = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "user": "alice",
            }

            # A real server would do HTTP 302 to redirect_uri?code=...&state=...
            # We return the destination so the attacker can read the code directly
            redirect_to = f"{redirect_uri}?code={code}&state={state}"
            self.send_json(200, {
                "code": code,
                "redirect_to": redirect_to,
                "note": "Server redirects victim to redirect_uri with the auth code",
            })
            return

        if path == "/oauth/token":
            grant_type = data.get("grant_type", "")
            code = data.get("code", "")
            redirect_uri = data.get("redirect_uri", "")
            client_id = data.get("client_id", "")
            client_secret = data.get("client_secret", "")

            if grant_type != "authorization_code":
                self.send_json(400, {"error": "unsupported_grant_type"})
                return
            if client_id not in CLIENTS:
                self.send_json(400, {"error": "invalid_client"})
                return
            if CLIENTS[client_id]["secret"] != client_secret:
                self.send_json(401, {"error": "invalid_client_secret"})
                return

            pending = PENDING_CODES.pop(code, None)
            if not pending:
                self.send_json(400, {"error": "invalid_code"})
                return

            access_token = secrets.token_hex(32)
            ACCESS_TOKENS[access_token] = {"user": pending["user"]}
            self.send_json(200, {
                "access_token": access_token,
                "token_type": "Bearer",
                "scope": "read",
            })
            return

        self.send_json(404, {"error": "not_found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
