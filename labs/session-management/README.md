# Session Management

A note-keeping app that assigns session tokens in sequence. Admin got token 1. Figure out the pattern and take their session.

## Quick Start

```
docker compose up --build
```

Then run the exploit:

```
python3 exploit/exploit.py http://localhost:8080
```

## What You Will Find

The app issues session tokens as `session_1`, `session_2`, and so on. The admin account was created at startup and received `session_1`. Any user who registers later can observe their own token number and deduce that the first token belongs to admin.

## Lab Structure

```
session-management/
  lab/          Dockerfile + app.py (the vulnerable server)
  exploit/      exploit.py (the working attack)
  docs/         background reading
  solutions/    walkthrough with full output
  test.sh       CI harness
```

## Prerequisites

- Docker with Compose
- Python 3.9+
