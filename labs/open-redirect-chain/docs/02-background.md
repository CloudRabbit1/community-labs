# 02: Background

## OAuth 2.0 authorization code flow

OAuth lets a user (Alice) grant a third-party app (CorpApp) access to their account at a service (BankOAuth) without sharing their password.

The flow:

1. CorpApp sends Alice to `GET /oauth/authorize?client_id=trusted-app&redirect_uri=...&response_type=code`
2. Alice clicks "Allow" at the authorization server.
3. The authorization server redirects Alice to `redirect_uri?code=AUTHCODE`.
4. CorpApp receives the code at the callback, exchanges it for an access token at `POST /oauth/token`.
5. CorpApp uses the access token to call the API on Alice's behalf.

The authorization code is a short-lived credential. Whoever receives it can exchange it for an access token. If an attacker captures the code, they can impersonate Alice.

## redirect_uri and security

The redirect_uri is the address where the authorization code lands. The spec (RFC 6749, section 10.6) requires that the authorization server validate redirect_uri before redirecting. Without this check, an attacker can direct the code anywhere.

The common mistake is validating by prefix:

```
# Registered: http://app.example.com/callback
# Attacker submits: http://app.example.com/callback/../../../evil
# or:              http://app.example.com.evil.com/callback
# or (this lab):   http://app.example.com/callback/../go?to=http://attacker
```

RFC 6749 and RFC 9700 both require exact-match validation for public clients.

## Open redirects

An open redirect is an endpoint that follows a user-supplied destination with no validation:

```python
@app.get('/go')
def go():
    return redirect(request.args.get('to', '/'))
```

Attackers use these for phishing: `https://trusted.example.com/go?to=https://evil.com`. Browsers display the trusted domain in the address bar before the redirect fires, making the link look legitimate.

In an OAuth chain, the open redirect does not need to look convincing. Its only job is to forward the browser with the code parameter still in the URL.
