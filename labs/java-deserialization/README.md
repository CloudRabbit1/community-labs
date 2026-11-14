# Deserialization Attack Lab

A hands-on lab demonstrating untrusted deserialization vulnerabilities. The app accepts pickled session blobs without validation, allowing an attacker to forge admin sessions and execute arbitrary code.

**Vulnerability class:** Insecure deserialization (OWASP A08:2021)
**Difficulty:** Intermediate
**Flags:** 2

---

## What You Will Learn

- How serialization is used to persist application state
- Why deserializing untrusted bytes is equivalent to remote code execution
- How to forge a privileged session using a benign payload
- How the `__reduce__` protocol enables arbitrary command execution
- Defense patterns: allowlisting types, using safer formats like JSON

---

## Prerequisites

- Docker and Docker Compose
- Python 3 (for crafting payloads)
- `curl`

---

## Quick Start

```bash
docker compose up --build -d
```

The app listens on `http://127.0.0.1:8091`.

---

## Lab Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login` | POST | Log in as alice (password: alice123) |
| `/api/profile` | GET | View profile; admin role reveals flag 1 |
| `/api/session/save` | GET | Serialize the current session to a blob |
| `/api/session/restore` | POST | Restore session from a pickled blob |
| `/api/admin/secret` | GET | Admin-only endpoint returning flag 2 |

---

## Goal

1. Forge an admin session by crafting a malicious pickle blob.
2. Use the admin session to read flag 1 from `/api/profile`.
3. Read flag 2 from `/api/admin/secret`.
4. (Bonus) Use `__reduce__` to execute a shell command inside the container.

---

## Automated Exploit

```bash
python3 exploit/exploit.py
```

---

## Teardown

```bash
docker compose down
```
