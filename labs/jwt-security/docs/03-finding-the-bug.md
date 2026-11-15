# Finding the Bug

Start the lab and confirm the service is running:

```bash
docker compose up --build -d
curl http://localhost:8081/
```

Output:
```json
{
  "service": "AuthApp v1.0",
  "endpoints": [
    "POST /login  {\"username\": \"...\", \"password\": \"...\"} -> token",
    "GET  /admin  Authorization: Bearer <token>          -> flag"
  ]
}
```

Log in with the provided credentials and capture the token:

```bash
curl -s -X POST http://localhost:8081/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}'
```

Output:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIiLCJyb2xlIjoidXNlciJ9.XXXXXX"
}
```

Decode the header and payload in Python:

```python
import base64, json

def b64d(s):
    pad = 4 - len(s) % 4
    return json.loads(base64.urlsafe_b64decode(s + "=" * (pad % 4)))

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIiLCJyb2xlIjoidXNlciJ9.XXXXXX"
parts = token.split(".")
print(b64d(parts[0]))  # {"alg": "HS256", "typ": "JWT"}
print(b64d(parts[1]))  # {"username": "user", "role": "user"}
```

The payload contains `username`. If the server uses the token's algorithm field without restriction, changing `alg` to `none` lets us remove the signature entirely. If the server accepts it, we can forge any `username` we want.

Confirm the user token is blocked on `/admin`:

```bash
curl -s http://localhost:8081/admin \
  -H "Authorization: Bearer <your_token>"
```

Output:
```json
{"error": "admin only"}
```

The endpoint exists. It just needs `username=admin` in the payload.
