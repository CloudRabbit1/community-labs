# Epoch

| Field | Value |
|-------|-------|
| Technique | OS command injection via unsanitized timestamp parameter |
| Target | UNIX timestamp conversion tool |
| Difficulty | Easy |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The `/convert` endpoint takes a `ts` parameter and builds a shell command string: `date -d @<ts>`. The input is not sanitized. Appending `;cat /flag.txt` to the timestamp value injects a second command that reads the flag.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/epoch
docker compose up --build -d
```
