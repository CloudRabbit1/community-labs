# Modern Web Stacks

| Field | Value |
|-------|-------|
| Technique | Middleware bypass via trusted internal header (CVE-2025-29927 style) |
| Target | Next.js-style application with middleware authentication |
| Difficulty | Easy |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The application uses a middleware layer to check authentication before allowing access to `/admin`. The middleware checks the `x-middleware-subrequest` header: if it equals `"middleware"`, the request is assumed to have already been processed and the auth check is skipped.

Sending `GET /admin` with `x-middleware-subrequest: middleware` bypasses the check and returns the flag without credentials.

This mirrors CVE-2025-29927, a vulnerability in real Next.js versions that allowed the same bypass against any middleware-protected route.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/modern-web-stacks
docker compose up --build -d
```
