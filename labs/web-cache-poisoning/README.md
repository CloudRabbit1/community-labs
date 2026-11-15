# Web Cache Poisoning Lab

A hands-on lab demonstrating web cache poisoning via the `X-Forwarded-Host` header. The app caches responses by URL path only, ignoring unkeyed headers. An attacker poisons the cache with a response that includes attacker-controlled URLs, which are then served to all subsequent visitors.

**CVE anchor:** CVE-2018-6389 / PortSwigger Research (web cache poisoning class)
**Difficulty:** Beginner-Intermediate
**Flags:** 2

---

## What You Will Learn

- How web caches work and what a cache key is
- Why unkeyed headers are a poisoning attack surface
- How to poison a cache with a single crafted request
- How the poisoned response reaches victims who never sent the malicious header
- Defense: add all reflected headers to the cache key or strip them at the cache layer

---

## Prerequisites

- Docker and Docker Compose
- `curl`

---

## Quick Start

```bash
docker compose up --build -d
```

The app listens on `http://127.0.0.1:8094`.

---

## Lab Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/home` | GET | Cached page; uses X-Forwarded-Host for asset URLs |
| `/api/data` | GET | Cached API response; also uses X-Forwarded-Host |
| `/admin` | GET | Returns flag 2 when cache is poisoned |
| `/cache/clear` | POST | Reset the cache |
| `/cache/stats` | GET | View current cache entries |

---

## Goal

1. Poison the `/home` cache by injecting `X-Forwarded-Host: attacker.com`.
2. Confirm that a victim request (without the injected header) receives the poisoned response.
3. Collect flag 1 (returned on the poisoning request) and flag 2 from `/admin`.

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
