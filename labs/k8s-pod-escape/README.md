# Kubernetes Pod Escape

Escalating from code execution inside a Kubernetes pod to node-level data access via hostPath volume and proc filesystem exposure.

## What you will learn

- What information is exposed inside a Kubernetes pod via /proc/self
- How a misconfigured hostPath volume gives a pod access to node-level data
- The core concept behind CVE-2024-21626 (Leaky Vessels / runc CWD escape)

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
| Lab app | 127.0.0.1:8099 |

## Teardown

```bash
docker compose down
```
