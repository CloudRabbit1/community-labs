# CRLF Injection

HTTP response header injection via unsanitized redirect parameter.

## What you will learn

- How CR (`\r`) and LF (`\n`) characters split HTTP header blocks
- How an injected header turns into an arbitrary `Set-Cookie` or `X-Custom-Header`
- Why frameworks like Flask strip these characters and why raw servers do not

## Prerequisites

- Docker and Docker Compose
- Python 3 (for the exploit script)
- curl

## Quick start

```bash
docker compose up --build -d
# wait ~3 seconds for the server to start
python3 exploit/exploit.py
```

Both flags are printed to the terminal.

## Ports

| Service | Host port |
|---------|-----------|
| Lab app | 127.0.0.1:8096 |

## Teardown

```bash
docker compose down
```
