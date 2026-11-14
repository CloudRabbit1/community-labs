# CVE-2025-25227: Joomla MFA Authentication Bypass

## What This Lab Is About

Multi-factor authentication is only as strong as the check that enforces it. CVE-2025-25227
is a missing server-side state check in Joomla 5.x. After logging in with a password, the
server flags the session as `mfa_pending` and routes the client through a TOTP challenge.
Admin routes are supposed to require both `state == "logged_in"` and `mfa_verified == True`.
The bug is that they only check the first condition. Send the login token directly to an
admin route and the MFA check never runs.

No exploit tooling is needed. One POST request to log in, one GET request to the admin
endpoint. The flag is returned on the second request.

## Lab Setup

```bash
docker compose up --build
```

The app starts on `http://localhost:8080` and simulates a Joomla 5.2.5 admin panel.
