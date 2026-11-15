# Defense

## Validate redirect_uri Against the Registered Whitelist

The fix is one check at the authorization endpoint:

```python
client = CLIENTS[client_id]
if redirect_uri not in client["registered_uris"]:
    return error(400, "redirect_uri_mismatch")
```

If the submitted URI does not exactly match a registered value, reject the request before issuing a code.

## Exact String Match Only

Prefix matching is dangerous. `http://app.example.com` matching `http://app.example.com.evil.com` is a known bypass. Use exact string equality, or a strict whitelist with no wildcards.

## Bind the Code to the redirect_uri

At the token exchange step, re-verify that the `redirect_uri` in the token request matches the one used in the authorization request:

```python
if redirect_uri != pending["redirect_uri"]:
    return error(400, "redirect_uri_mismatch")
```

This is a defense-in-depth measure. If the original check is bypassed, the code cannot be redeemed at a different URI.

## Use PKCE for Public Clients

For mobile and single-page apps that cannot keep a `client_secret`, Proof Key for Code Exchange (PKCE) ties the code to a code verifier that only the original requester knows, making a stolen code useless.
