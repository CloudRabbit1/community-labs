"""
Azure lateral movement simulation.

Three services in one process:

  /metadata/identity/oauth2/token   — Azure IMDS: returns a signed JWT
  /secrets/<name>                   — Azure Key Vault: requires Bearer JWT,
                                      returns the storage access key
  /blob/<container>/<path>          — Azure Blob Storage: requires ?key=...,
                                      returns the flag

The student chains all three to reach the flag.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# ---- Secrets (generated at container start by setup.sh) ----
STORAGE_KEY = open("/storage_key.txt").read().strip()
FLAG        = open("/flag.txt").read().strip()

# ---- JWT signing key (fixed per process, unknown to student) ----
JWT_SECRET = os.urandom(32)


# ── Minimal HS256 JWT ──────────────────────────────────────────────────────

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_token(resource: str) -> str:
    header  = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url(json.dumps({
        "sub": "vm1-managed-identity",
        "aud": resource,
        "iss": "https://sts.windows.net/00000000-0000-0000-0000-000000000000/",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }).encode())
    sig = _b64url(hmac.new(JWT_SECRET, f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


def verify_token(token: str, expected_aud: str) -> bool:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return False
        header_payload = f"{parts[0]}.{parts[1]}"
        expected_sig = _b64url(
            hmac.new(JWT_SECRET, header_payload.encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(parts[2], expected_sig):
            return False
        pad = "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad))
        return payload.get("aud") == expected_aud and payload.get("exp", 0) > time.time()
    except Exception:
        return False


# ── HTTP handler ──────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text, status=200):
        body = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def bearer_token(self) -> str:
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return ""

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        # ── Hop 1: Azure IMDS ──────────────────────────────────────────
        if parsed.path == "/metadata/identity/oauth2/token":
            if self.headers.get("Metadata", "").lower() != "true":
                self.send_json({"error": "Missing required header: Metadata: true"}, 400)
                return
            resource = qs.get("resource", ["https://vault.azure.net"])[0]
            token = make_token(resource)
            self.send_json({
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": "3600",
                "resource": resource,
            })

        # ── Hop 2: Azure Key Vault ─────────────────────────────────────
        elif parsed.path.startswith("/secrets/"):
            token = self.bearer_token()
            if not verify_token(token, "https://vault.azure.net"):
                self.send_json({"error": {"code": "Unauthorized", "message": "Invalid token"}}, 401)
                return
            secret_name = parsed.path.split("/secrets/")[1].rstrip("/")
            if secret_name == "storage-access-key":
                self.send_json({
                    "id": "https://lab-vault.vault.azure.net/secrets/storage-access-key/1",
                    "value": STORAGE_KEY,
                    "attributes": {"enabled": True},
                })
            else:
                self.send_json({"error": {"code": "SecretNotFound"}}, 404)

        # ── Hop 3: Azure Blob Storage ──────────────────────────────────
        elif parsed.path.startswith("/blob/"):
            key = qs.get("key", [None])[0]
            if key != STORAGE_KEY:
                self.send_text("AuthenticationFailed\nServer failed to authenticate the request.", 403)
                return
            if "/flag.txt" in parsed.path:
                self.send_text(FLAG)
            else:
                self.send_text("BlobNotFound", 404)

        # ── Info page ──────────────────────────────────────────────────
        else:
            self.send_text(
                "Azure Lateral Movement Lab\n\n"
                "Available endpoints:\n"
                "  GET /metadata/identity/oauth2/token?resource=https://vault.azure.net\n"
                "      Header: Metadata: true\n"
                "      => returns access_token\n\n"
                "  GET /secrets/storage-access-key?api-version=7.4\n"
                "      Header: Authorization: Bearer <access_token>\n"
                "      => returns storage access key\n\n"
                "  GET /blob/labcontainer/flag.txt?key=<storage_key>\n"
                "      => returns the flag\n"
            )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[*] Lab running on port {port}")
    server.serve_forever()
