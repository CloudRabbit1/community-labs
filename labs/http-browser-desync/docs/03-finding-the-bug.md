# Finding the Bug

Start the lab:

```bash
docker compose up --build -d
curl http://localhost:8080/
```

Output:
```json
{"status": "ok", "path": "/"}
```

Confirm the frontend blocks `/admin`:

```bash
curl -v http://localhost:8080/admin
```

Output:
```
< HTTP/1.1 403 Forbidden
{"error":"forbidden","note":"admin is not accessible from the public interface"}
```

Look at how the frontend handles body length in `lab/app.py`:

```python
cl = int(headers.get("content-length", "0"))
body = extra
while len(body) < cl:
    chunk = conn.recv(cl - len(body))
    ...
body = body[:cl]
backend.sendall(header_bytes + b"\r\n\r\n" + body)
```

The frontend reads exactly CL bytes and forwards them verbatim. It does not strip or override the `Transfer-Encoding` header. The backend receives both CL and TE headers.

Look at the backend:

```python
te = headers.get("transfer-encoding", "").lower()
if "chunked" in te:
    body = body[:cl]
    leftovers = b""
    if b"0\r\n\r\n" in body:
        term_idx = body.index(b"0\r\n\r\n") + 5
        leftovers = body[term_idx:]
    if b"GET /admin" in leftovers:
        # returns flag
```

The backend uses TE when both headers are present. It stops at `0\r\n\r\n` and treats everything after as a new request. If that new request is `GET /admin`, it returns the flag.

The gap: the frontend counts 43 bytes from the body, but only the first 5 bytes (`0\r\n\r\n`) are the legitimate chunked body. The other 38 bytes are the smuggled request the attacker injected.
