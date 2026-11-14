# mass-assignment: JSON over-posting escalates user role to admin

Log in as a regular user, then send a PUT request to your own profile with `"role": "admin"` in the body. The server merges the entire request object without filtering sensitive fields. Your session role changes immediately, granting access to admin endpoints.

> This container binds to `127.0.0.1` only.

CVE anchor: CVE-2023-35933 (Payload CMS mass assignment via REST API).

## Quick start

```bash
docker compose up --build -d
until nc -z -w2 127.0.0.1 8084 2>/dev/null; do sleep 1; done && echo "ready"
```

## Attack path

| Step | Action | Result |
|------|--------|--------|
| 1 | POST /login with valid user credentials | Session cookie |
| 2 | PUT /api/user/profile with `{"role": "admin"}` | Role escalated |
| 3 | GET /admin | Flag 1 |
| 4 | GET /admin/secrets | Flag 2 |

## Docs

```
docs/01-introduction.md
docs/02-background.md
docs/03-finding-the-bug.md
docs/04-exploitation.md
docs/05-defense.md
```

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose
- curl or Python 3
