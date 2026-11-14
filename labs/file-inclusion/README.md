# File Inclusion

| Field | Value |
|-------|-------|
| Technique | Local file inclusion via unsanitized path parameter |
| Target | Static page reader web app |
| Difficulty | Medium |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The `/?page=` parameter reads files from a `pages/` directory. The path is joined with the directory name without sanitization, so `../../flag.txt` escapes the directory and reads `/flag.txt`.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/file-inclusion
docker compose up --build -d
```
