# HTTP Browser Desync

| Field | Value |
|-------|-------|
| Technique | CL.TE HTTP request smuggling |
| Target | Frontend/backend pair with conflicting body-length parsers |
| Difficulty | Hard |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The frontend proxy reads request bodies using Content-Length. The backend parses Transfer-Encoding: chunked. When a request includes both headers, the two servers disagree on where the body ends.

The exploit sends a POST with `Content-Length: 43` and `Transfer-Encoding: chunked`. The 43-byte body contains a chunked terminator (`0\r\n\r\n`) followed by a raw `GET /admin` request. The frontend reads all 43 bytes as the body and forwards them. The backend's chunked parser stops at the terminator, then sees the remaining bytes as a smuggled HTTP request and returns the flag.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/http-browser-desync
docker compose up --build -d
```
