"""
Encryption oracle — simulates a service that appends a secret to your
input before encrypting with AES-ECB. The secret is the lab flag.

Endpoint: GET /encrypt?input=<your_bytes_as_latin1>
Response: {"ciphertext": "<base64>"}
"""

import os
import base64
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote_to_bytes

KEY = os.urandom(16)
SECRET = open("/flag.txt", "rb").read().strip()


def pkcs7(data: bytes, block: int = 16) -> bytes:
    n = block - (len(data) % block)
    return data + bytes([n] * n)


def aes_ecb_encrypt(key: bytes, plaintext: bytes) -> bytes:
    # Pure Python AES-ECB via the standard library ssl/ctypes path is unavailable;
    # use the os-level openssl command to stay dependency-free inside the image.
    import subprocess, tempfile, os as _os
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(plaintext)
        f.flush()
        result = subprocess.run(
            ["openssl", "enc", "-aes-128-ecb", "-nosalt", "-nopad",
             "-K", key.hex()],
            input=plaintext, capture_output=True
        )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())
    return result.stdout


HOME = b"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>Secure Encryption Service</title></head><body>
<h1>Secure Encryption Service</h1>
<p>Send your data to <code>/encrypt?input=your_data</code>.</p>
<p>We append a secret before encrypting with our unbreakable ECB cipher.</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silence access log

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/encrypt":
            qs = parse_qs(parsed.query, keep_blank_values=True)
            raw = qs.get("input", [b""])[0]
            if isinstance(raw, str):
                raw = raw.encode("latin-1")
            plaintext = pkcs7(raw + SECRET)
            ciphertext = aes_ecb_encrypt(KEY, plaintext)
            self.send_json({"ciphertext": base64.b64encode(ciphertext).decode()})
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(HOME)))
            self.end_headers()
            self.wfile.write(HOME)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[*] Oracle running on port {port}")
    server.serve_forever()
