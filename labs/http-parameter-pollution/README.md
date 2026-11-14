# HTTP Parameter Pollution

WAF bypass and access control bypass via duplicate HTTP query parameters.

## What you will learn

- How different parts of a framework read the same parameter differently
- How sending `?id=safe&id=injection` lets a payload past a WAF
- How duplicate role parameters bypass an access control check

## Prerequisites

- Docker and Docker Compose
- Python 3 with the `requests` library (`pip install requests`)

## Quick start

```bash
docker compose up --build -d
# wait ~4 seconds
python3 exploit/exploit.py
```

Both flags are printed to the terminal.

## Ports

| Service | Host port |
|---------|-----------|
| Lab app | 127.0.0.1:8098 |

## Teardown

```bash
docker compose down
```
