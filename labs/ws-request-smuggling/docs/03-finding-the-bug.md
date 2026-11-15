# Finding the Bug

Start the lab and confirm the service is running:

```bash
docker compose up --build -d
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

Confirm the frontend blocks direct access to `/admin`:

```bash
curl -v http://localhost:8080/admin
```

Output:
```
< HTTP/1.1 403 Forbidden
{"error":"forbidden","note":"admin is not accessible from the public interface"}
```

The frontend enforces a 403. The backend presumably has an `/admin` endpoint that returns something sensitive.

Now look at how the proxy handles WebSocket traffic. The key question: does the proxy validate WebSocket frames after the handshake, or does it pass raw bytes?

In `lab/app.py`, the `handle_frontend` function upgrades the connection and then starts two threads that call `pipe()`:

```python
def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
```

No frame parsing. No opcode checking. Raw bytes from the client go directly to the backend socket. If you send a raw HTTP request after the handshake, the backend receives it as HTTP.
