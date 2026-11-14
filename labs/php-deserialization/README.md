# PHP Deserialization Lab

A hands-on lab demonstrating PHP object injection via `unserialize()`. The app deserializes attacker-supplied session blobs without validation, enabling privilege escalation and magic method gadget chains.

**Vulnerability class:** PHP Object Injection / Insecure Deserialization (OWASP A08:2021)
**Difficulty:** Intermediate
**Flags:** 2

---

## What You Will Learn

- How PHP serialization works and what `unserialize()` does
- How to forge a PHP serialized array to escalate privileges
- How magic methods (`__destruct`, `__wakeup`, `__toString`) are triggered by `unserialize()`
- How to chain gadget classes to achieve arbitrary file writes
- Defense: use JSON + HMAC instead of serialized objects

---

## Prerequisites

- Docker and Docker Compose
- Python 3 or `curl`

---

## Quick Start

```bash
docker compose up --build -d
```

The app listens on `http://127.0.0.1:8092`.

---

## Lab Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/login` | POST | Log in as alice (password: alice123) |
| `/profile` | GET | View profile; admin role reveals flag 1 |
| `/session/save` | POST | Serialize the current session to a blob |
| `/session/restore` | POST | Restore session from a serialized blob |
| `/admin/secret` | GET | Admin-only endpoint returning flag 2 |

---

## Goal

1. Forge a PHP serialized admin session to read flag 1 from `/profile`.
2. Use the admin session to read flag 2 from `/admin/secret`.
3. (Bonus) Trigger the `Logger.__destruct` gadget to write an arbitrary file.

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
