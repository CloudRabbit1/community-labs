#!/usr/bin/env python3
"""
HTTP Browser Desync. Demonstrates CL.TE request smuggling.

The frontend on port 8080 uses Content-Length to determine where a request
body ends. It forwards the raw request to the backend on port 9001. The
backend parses Transfer-Encoding: chunked. When both headers are present,
they disagree on how much of the body belongs to this request. Bytes that
the frontend considers part of the body but the backend considers trailing
garbage after the chunked body are interpreted by the backend as the start
of a new HTTP request.
"""
import json
import os
import socket
import threading

FLAG = open("/flag.txt").read().strip()

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 9001


def recv_until(sock, terminator, maxbuf=65536):
    buf = b""
    while terminator not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            return buf, b""
        buf += chunk
        if len(buf) > maxbuf:
            break
    idx = buf.index(terminator)
    return buf[:idx], buf[idx + len(terminator):]


def parse_headers(raw_bytes):
    text = raw_bytes.decode(errors="replace")
    lines = text.split("\r\n")
    request_line = lines[0]
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            headers[k.lower()] = v
    return request_line, headers


def send_json(conn, status, data):
    body = json.dumps(data)
    conn.sendall(
        f"HTTP/1.1 {status}\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
    )


# Backend: parses Transfer-Encoding: chunked
# Any bytes after "0\r\n\r\n" are treated as the start of the next request.
def handle_backend(conn, addr):
    try:
        header_bytes, extra = recv_until(conn, b"\r\n\r\n")
        if not header_bytes:
            return
        request_line, headers = parse_headers(header_bytes)
        path = request_line.split(" ")[1] if " " in request_line else "/"
        te = headers.get("transfer-encoding", "").lower()
        cl = int(headers.get("content-length", "0"))

        if "chunked" in te:
            # Read the body, governed by content-length (the frontend forwarded
            # exactly that many bytes).
            body = extra
            conn.settimeout(2)
            try:
                while len(body) < cl:
                    chunk = conn.recv(cl - len(body))
                    if not chunk:
                        break
                    body += chunk
            except socket.timeout:
                pass
            body = body[:cl]

            # Find the chunked terminator
            leftovers = b""
            if b"0\r\n\r\n" in body:
                term_idx = body.index(b"0\r\n\r\n") + 5
                leftovers = body[term_idx:]

            if b"GET /admin" in leftovers:
                # Smuggled request detected in the leftover bytes
                send_json(conn, "200 OK", {"status": "smuggled", "flag": FLAG})
            else:
                send_json(conn, "200 OK", {"status": "ok", "path": path})

        elif path == "/admin":
            # Direct admin access (backend has no frontend ACL enforcement)
            send_json(conn, "200 OK", {"status": "admin", "flag": FLAG})

        else:
            send_json(conn, "200 OK", {"status": "ok", "path": path})

    except Exception:
        pass
    finally:
        conn.close()


# Frontend: reads Content-Length bytes and forwards raw request to backend
def handle_frontend(conn, addr):
    try:
        header_bytes, extra = recv_until(conn, b"\r\n\r\n")
        if not header_bytes:
            return
        request_line, headers = parse_headers(header_bytes)
        path = request_line.split(" ")[1] if " " in request_line else "/"
        cl = int(headers.get("content-length", "0"))

        if "/admin" in path:
            send_json(conn, "403 Forbidden", {
                "error": "forbidden",
                "note": "admin is not accessible from the public interface"
            })
            return

        # Read exactly Content-Length bytes of body
        body = extra
        conn.settimeout(2)
        try:
            while len(body) < cl:
                chunk = conn.recv(cl - len(body))
                if not chunk:
                    break
                body += chunk
        except socket.timeout:
            pass
        body = body[:cl]

        # Forward the raw request (headers + body) to the backend.
        # Both Content-Length and Transfer-Encoding headers are forwarded as-is.
        backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend.connect((BACKEND_HOST, BACKEND_PORT))
        backend.sendall(header_bytes + b"\r\n\r\n" + body)

        # Read backend response
        backend_resp = b""
        backend.settimeout(3)
        try:
            while True:
                chunk = backend.recv(4096)
                if not chunk:
                    break
                backend_resp += chunk
        except socket.timeout:
            pass
        backend.close()

        conn.sendall(backend_resp if backend_resp else b"HTTP/1.1 502 Bad Gateway\r\n\r\n")

    except Exception:
        pass
    finally:
        conn.close()


def run_server(host, port, handler):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(50)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handler, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    threading.Thread(
        target=run_server,
        args=(BACKEND_HOST, BACKEND_PORT, handle_backend),
        daemon=True
    ).start()
    print(f"Backend listening on {BACKEND_HOST}:{BACKEND_PORT}", flush=True)
    print("Frontend listening on 0.0.0.0:8080", flush=True)
    run_server("0.0.0.0", 8080, handle_frontend)
