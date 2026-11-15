# XSS Introduction

A community comment board that renders user input without escaping. An admin bot visits the page every two seconds with a privileged session cookie. Inject a script to steal it.

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## What You Learn

- How stored XSS works: input stored on the server, executed in every visitor's browser
- Why HTML escaping is non-negotiable before rendering user content
- How an XSS payload steals session cookies via fetch or document.location

## Lab Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Comment board (renders comments unescaped) |
| `POST /comment` | Submit a comment |
| `GET /steal?c=<value>` | Cookie theft endpoint (called by the XSS payload) |
| `GET /stolen` | Returns the last captured cookie value |

## Prerequisites

- Docker and Docker Compose
- Python 3.x (for the exploit)
