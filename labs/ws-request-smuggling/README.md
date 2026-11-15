# WebSocket Request Smuggling

| Field | Value |
|-------|-------|
| Technique | WebSocket request smuggling via unvalidated byte pipe |
| Target | WebSocket proxy with blind byte forwarding |
| Difficulty | Medium |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The proxy on port 8080 upgrades HTTP connections to WebSocket and pipes all bytes to a backend on port 9000. After the handshake, the proxy does no WebSocket frame validation. It passes raw bytes from the client directly to the backend socket.

The backend treats those bytes as a new HTTP request. Sending `GET /admin HTTP/1.1` through the tunnel after the handshake reaches the backend as a direct HTTP request, bypassing the frontend's 403 on `/admin`.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/ws-request-smuggling
docker compose up --build -d
```
