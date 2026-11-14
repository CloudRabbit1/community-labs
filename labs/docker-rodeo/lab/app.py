#!/usr/bin/env python3
"""
Docker socket exposure via management API.

This app acts as a Docker management dashboard. It exposes HTTP endpoints
that proxy directly to the host's Docker daemon via the mounted socket at
/var/run/docker.sock. Any client that can reach port 8080 can create
privileged containers, mount volumes, and escape the container boundary.
"""
import json
import socket as _socket
import struct
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

DOCKER_SOCK = "/var/run/docker.sock"


def _decode_chunked(data: bytes) -> bytes:
    result = b""
    while data:
        idx = data.find(b"\r\n")
        if idx == -1:
            break
        try:
            size = int(data[:idx].split(b";")[0].strip(), 16)
        except ValueError:
            break
        if size == 0:
            break
        result += data[idx + 2: idx + 2 + size]
        data = data[idx + 2 + size + 2:]
    return result


def demux_stream(data: bytes) -> str:
    """Decode Docker multiplexed log stream (8-byte frame headers)."""
    out = b""
    while len(data) >= 8:
        frame_type = data[0]
        size = struct.unpack(">I", data[4:8])[0]
        payload = data[8: 8 + size]
        if frame_type in (1, 2):
            out += payload
        data = data[8 + size:]
    if not out and data:
        out = data
    return out.decode(errors="replace")


def docker_request(method: str, path: str, body=None, timeout: int = 30) -> tuple:
    s = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(DOCKER_SOCK)

    if body is not None:
        body_bytes = json.dumps(body).encode()
        hdrs = (
            f"{method} {path} HTTP/1.1\r\n"
            f"Host: localhost\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            f"Connection: close\r\n\r\n"
        )
        s.sendall(hdrs.encode() + body_bytes)
    else:
        hdrs = (
            f"{method} {path} HTTP/1.1\r\n"
            f"Host: localhost\r\n"
            f"Connection: close\r\n\r\n"
        )
        s.sendall(hdrs.encode())

    buf = b""
    while True:
        try:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
        except _socket.timeout:
            break
    s.close()

    sep = buf.find(b"\r\n\r\n")
    if sep == -1:
        return 0, b""

    header_section = buf[:sep].decode(errors="replace")
    resp_body = buf[sep + 4:]

    lines = header_section.split("\r\n")
    try:
        status_code = int(lines[0].split(" ")[1])
    except (IndexError, ValueError):
        status_code = 0

    headers_dict = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers_dict[k.strip().lower()] = v.strip()

    if headers_dict.get("transfer-encoding", "").lower() == "chunked":
        resp_body = _decode_chunked(resp_body)

    return status_code, resp_body


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code: int, data):
        b = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body(self) -> bytes:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    def proxy(self, method: str, docker_path: str, raw_body: bytes = None, timeout: int = 30):
        body_obj = None
        if raw_body:
            try:
                body_obj = json.loads(raw_body)
            except Exception:
                self.send_json(400, {"error": "invalid JSON body"})
                return

        try:
            code, resp = docker_request(method, docker_path, body=body_obj, timeout=timeout)
        except Exception as e:
            self.send_json(500, {"error": str(e)})
            return

        # Try to decode as JSON; fall back to text
        try:
            data = json.loads(resp)
        except Exception:
            data = demux_stream(resp) if resp else ""

        self.send_json(code, data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_json(200, {
                "service": "Docker Management Dashboard v1.0",
                "note": "Docker socket is mounted at /var/run/docker.sock",
                "endpoints": [
                    "GET  /api/docker/containers/json",
                    "POST /api/docker/containers/create",
                    "POST /api/docker/containers/{id}/start",
                    "POST /api/docker/containers/{id}/wait",
                    "GET  /api/docker/containers/{id}/logs?stdout=1",
                    "DELETE /api/docker/containers/{id}",
                ],
            })
            return

        if path.startswith("/api/docker/"):
            docker_path = path[len("/api/docker"):]
            if parsed.query:
                docker_path += "?" + parsed.query
            self.proxy("GET", docker_path)
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/docker/"):
            docker_path = path[len("/api/docker"):]
            if parsed.query:
                docker_path += "?" + parsed.query
            timeout = 35 if "/wait" in docker_path else 30
            self.proxy("POST", docker_path, self.body(), timeout=timeout)
            return

        self.send_json(404, {"error": "Not found"})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/docker/"):
            docker_path = path[len("/api/docker"):]
            self.proxy("DELETE", docker_path)
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
