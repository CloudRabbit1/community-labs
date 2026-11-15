# DOM-Based Attacks

| Field | Value |
|-------|-------|
| Technique | DOM-based XSS via innerHTML sink |
| Target | Search application with client-side rendering |
| Difficulty | Easy |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The `/reflect` endpoint injects the `q` query parameter directly into an HTML page via `innerHTML`. Anything you put in `q` runs as HTML in the browser. An attacker who can get a victim to click a crafted link can steal the victim's session cookie and use it to call `/api/flag`.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/dom-based-attacks
docker compose up --build -d
```
