# Hammer

| Field | Value |
|-------|-------|
| Technique | Rate-limit bypass via X-Forwarded-For rotation, then OTP brute force, then command allowlist bypass |
| Target | Password reset + command execution service |
| Difficulty | Medium |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The app protects its password reset OTP with a rate limit of 10 attempts per minute, keyed on the `X-Forwarded-For` header. Because the app trusts that header without validation, rotating the value for each attempt bypasses the limit entirely.

After brute-forcing the 4-digit OTP (0000-9999), the app returns a session token. The `/execute` endpoint then checks commands against an allowlist using `startswith()`. Sending `id; cat /flag.txt` passes the check because it starts with `id`.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/hammer
docker compose up --build -d
```
