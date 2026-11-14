#!/usr/bin/env python3
"""
WebSocket Chat Proxy. Demonstrates WebSocket request smuggling.

The frontend on port 8080 upgrades HTTP connections to WebSocket and
pipes bytes to the backend on port 9000. Because the proxy does no
WebSocket frame validation after the handshake, a client can send raw
HTTP requests through the tunnel. The backend receives them as new HTTP
requests, bypassing frontend access controls.
"""
import json
import os
import socket
import threading

FLAG = open("/flag.txt").read().strip()

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 9000


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


# Backend: internal admin API on 127.0.0.1:9000
# Not reachable directly from outside the container.
def handle_backend(conn, addr):
    try:
        header_bytes, extra = recv_until(conn, b"\r\n\r\n")
        if not header_bytes:
            return
        request_line, headers = parse_headers(header_bytes)
        upgrade = headers.get("upgrade", "").lower()

        if upgrade == "websocket":
            # Accept the WebSocket upgrade
            conn.sendall(
                b"HTTP/1.1 101 Switching Protocols\r\n"
                b"Upgrade: websocket\r\n"
                b"Connection: Upgrade\r\n"
                b"\r\n"
            )
            # Read post-upgrade data. This may be WebSocket frames or
            # smuggled raw HTTP from an attacker.
            buf = extra
            conn.settimeout(2.0)
            try:
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    buf += chunk
            except socket.timeout:
                pass

            # If the tunnel data looks like a raw HTTP request, process it.
            if buf.startswith(b"GET ") or buf.startswith(b"POST "):
                smug_line = buf.split(b"\r\n")[0].decode(errors="replace")
                if "/admin" in smug_line:
                    send_json(conn, "200 OK", {"status": "admin", "flag": FLAG})
                else:
                    send_json(conn, "403 Forbidden", {"error": "forbidden"})

        elif "/admin" in request_line:
            send_json(conn, "200 OK", {"status": "admin", "flag": FLAG})

        else:
            send_json(conn, "403 Forbidden", {
                "error": "forbidden",
                "note": "admin endpoint is not publicly accessible"
            })

    except Exception:
        pass
    finally:
        conn.close()


# Frontend: WebSocket proxy on 0.0.0.0:8080
def handle_frontend(conn, addr):
    try:
        header_bytes, extra = recv_until(conn, b"\r\n\r\n")
        if not header_bytes:
            return
        request_line, headers = parse_headers(header_bytes)
        upgrade = headers.get("upgrade", "").lower()
        path = request_line.split(" ")[1] if " " in request_line else "/"

        if upgrade == "websocket":
            # Proxy the upgrade to the backend
            backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            backend.connect((BACKEND_HOST, BACKEND_PORT))
            backend.sendall(header_bytes + b"\r\n\r\n" + extra)

            # Read the backend's 101 response
            backend_resp_headers, backend_extra = recv_until(backend, b"\r\n\r\n")
            if b"101" not in backend_resp_headers:
                backend.close()
                conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                return

            # Forward 101 to the client
            conn.sendall(backend_resp_headers + b"\r\n\r\n" + backend_extra)

            # Blindly pipe bytes in both directions.
            # No WebSocket frame validation: raw bytes pass through unmodified.
            # This allows a client to send raw HTTP requests through the tunnel.
            def pipe(src, dst):
                try:
                    while True:
                        data = src.recv(4096)
                        if not data:
                            break
                        dst.sendall(data)
                except Exception:
                    pass

            t1 = threading.Thread(target=pipe, args=(conn, backend), daemon=True)
            t2 = threading.Thread(target=pipe, args=(backend, conn), daemon=True)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            backend.close()

        elif "/admin" in path:
            send_json(conn, "403 Forbidden", {
                "error": "forbidden",
                "note": "admin is not accessible from the public interface"
            })

        elif path == "/":
            send_json(conn, "200 OK", {
                "service": "WebSocket Chat Proxy v1.0",
                "websocket_endpoint": "ws://localhost:8080/chat",
                "note": "Connect via WebSocket to use the chat service"
            })

        else:
            send_json(conn, "404 Not Found", {"error": "not found"})

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
