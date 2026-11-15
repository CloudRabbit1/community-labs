# Finding the Bug

## Enumerate the Endpoints

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

The app describes its own flow. Two steps: password, then OTP.

## Step Through the Login

Send valid credentials:

```
curl -s -X POST http://localhost:8080/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"password123"}' \
  -c /tmp/jar.txt -b /tmp/jar.txt
```

```json
{"status": "password accepted", "next": "POST /mfa with your OTP"}
```

The response sets a `pre_auth` cookie. The session is in an intermediate state: password accepted, MFA pending.

## Examine the OTP Challenge

There is no hint about where the OTP comes from. No QR code, no authenticator setup. The `/mfa` endpoint simply accepts a six-digit number.

That is the clue. A properly implemented TOTP system would have required a setup step where you enrolled a device. The absence of setup means the server is generating the OTP itself, and the only input available to it without a shared secret is the current time.

Hypothesis: `OTP = timestamp % 1000000`.
