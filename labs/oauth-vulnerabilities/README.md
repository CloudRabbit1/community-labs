# OAuth Vulnerabilities

| Field | Value |
|-------|-------|
| Technique | OAuth 2.0 open redirect via unvalidated redirect_uri |
| Target | OAuth authorization server |
| Difficulty | Medium |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The authorization server accepts any `redirect_uri` without checking it against the client's registered URIs. An attacker crafts a malicious authorization URL pointing victims to an attacker-controlled `redirect_uri`. The auth code lands at the attacker's server, where it is exchanged for an access token to read the victim's data.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/oauth-vulnerabilities
docker compose up --build -d
```
