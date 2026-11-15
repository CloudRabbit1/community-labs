# Host Header Injection: Password Reset Poisoning

A hands-on lab demonstrating how a web application that trusts the HTTP `Host` header without validation can be exploited to hijack password reset tokens.

**CVE anchor:** CVE-2024-28107 (illustrative; the class of vulnerability is universal)
**Difficulty:** Beginner-Intermediate
**Flags:** 2

---

## What You Will Learn

- How the HTTP `Host` header works and why it cannot be trusted
- How password reset poisoning works step by step
- How to intercept a reset token by controlling the email link's domain
- How to defend against this class of attack

---

## Prerequisites

- Docker and Docker Compose installed
- `curl` or a tool like Burp Suite
- Basic familiarity with HTTP requests

---

## Quick Start

```bash
docker compose up --build -d
```

The app listens on `http://127.0.0.1:8090`.

---

## Lab Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset-password` | POST | Request a password reset link |
| `/reset` | GET | Consume the reset token |
| `/login` | POST | Log in and receive flag 1 |
| `/admin-data` | GET | Admin-only data containing flag 2 |
| `/debug/last-email` | GET | Dev debug endpoint showing the last email sent |

---

## Goal

1. Use the `Host` header injection vulnerability to capture admin's reset token.
2. Reset the admin password.
3. Log in as admin to get flag 1.
4. Access `/admin-data` to get flag 2.

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
