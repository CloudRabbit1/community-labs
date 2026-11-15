# Surfer

| Field | Value |
|-------|-------|
| Technique | SSRF to internal admin panel |
| Target | URL preview service with unrestricted fetch |
| Difficulty | Easy |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The app provides a `/fetch?url=` endpoint that retrieves any URL and returns its content. It is intended for previewing external web pages, but nothing prevents the caller from supplying an internal address.

An admin service runs on `127.0.0.1:9000` inside the container. It is not exposed to the host. It checks that requests come from localhost before returning the flag. Because the app itself makes the request, the check passes.

Sending `GET /fetch?url=http://127.0.0.1:9000/admin` causes the server to fetch its own admin panel and return the flag to the attacker.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/surfer
docker compose up --build -d
```
