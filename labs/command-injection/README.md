# Command Injection

| Field | Value |
|-------|-------|
| Technique | OS command injection via unsanitized shell input |
| Target | Network diagnostic ping helper |
| Difficulty | Easy |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The `/ping` endpoint takes a `host` parameter and builds a shell command string without sanitizing the input. Appending `;cat /flag.txt` to the host value causes the server to execute both `ping` and `cat` as separate shell commands.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/command-injection
docker compose up --build -d
```
