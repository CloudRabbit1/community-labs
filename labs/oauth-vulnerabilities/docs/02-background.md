# Background

## OAuth 2.0 Authorization Code Flow

1. The application redirects the user to the authorization server with `client_id`, `redirect_uri`, and `state`.
2. The user approves access.
3. The authorization server redirects the user back to `redirect_uri` with a short-lived `code`.
4. The application exchanges `code` + `client_secret` at `/oauth/token` for an `access_token`.
5. The application uses the `access_token` to call protected APIs.

## Why redirect_uri Validation Matters

The `code` is the key to the whole flow. If the authorization server sends it to the wrong destination, whoever receives it can complete step 4 and get the token. The only control is that `redirect_uri` must match a URI the application owner registered in advance.

RFC 6749 section 10.6 is explicit: the authorization server MUST validate `redirect_uri` against the registered value, and if they do not match, it MUST reject the request.

## The Attack

An attacker registers no client. They reuse a known `client_id` but supply their own `redirect_uri`. The user clicks a link, approves access (or is tricked into it), and the code lands on the attacker's server. The attacker uses the legitimate `client_secret` (often embedded in a public app) to exchange the code for a token.
