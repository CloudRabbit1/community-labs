# Open Redirect Chain

OAuth authorization code theft via chained open redirect and weak redirect_uri validation.

## What you will learn

- Why OAuth redirect_uri must use exact-match validation, not prefix matching
- How an open redirect on a trusted domain breaks OAuth security
- How to chain two low-severity flaws into an account-takeover attack

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
| Lab app | 127.0.0.1:8097 |

## Teardown

```bash
docker compose down
```
