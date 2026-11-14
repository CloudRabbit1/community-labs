# 05: Defense

## Fix 1: exact-match redirect_uri validation

Replace prefix matching with exact matching:

```python
# VULNERABLE: prefix match
if not redirect_uri.startswith(client['redirect_prefix']):
    raise BadRequest('invalid_redirect_uri')

# FIXED: exact match against a registered set
CLIENTS = {
    'trusted-app': {
        'secret': 'client-secret-xyz',
        'allowed_redirect_uris': {
            'http://127.0.0.1:8097/client/callback',
        },
    }
}

if redirect_uri not in client['allowed_redirect_uris']:
    raise BadRequest('invalid_redirect_uri')
```

With exact matching, `http://127.0.0.1:8097/client/go?to=...` is not in the allowed set and the attack is blocked at the first step.

## Fix 2: eliminate the open redirect

Validate the destination before redirecting:

```python
ALLOWED_INTERNAL = {'/home', '/dashboard', '/profile'}

@app.get('/client/go')
def client_go():
    to = request.args.get('to', '/')
    # Only allow relative paths from an allowlist
    if to not in ALLOWED_INTERNAL:
        to = '/home'
    return redirect(to)
```

If navigation to external URLs is required, map them through an explicit allowlist or a signed token so attackers cannot supply arbitrary destinations.

## Why both fixes are needed

Each fix alone reduces the attack surface:

- Exact redirect_uri validation alone: the attack stops at the OAuth server. The open redirect still exists but cannot be weaponized via OAuth.
- Removing the open redirect alone: the OAuth prefix check is still weak, but there are no exploitable endpoints starting with `/client` that forward to attacker-controlled URLs.

Defense in depth requires both. A future open redirect introduced by a developer would re-enable the attack if only the OAuth fix is applied.

## Automated detection

- Static analysis tools (Semgrep, CodeQL) have rules for `redirect(request.args.get(...))` patterns.
- Dynamic scanners test for `?redirect=http://evil.com` and `?to=//evil.com` payloads in all parameters.
- OAuth security reviews should specifically verify that redirect_uri is exact-matched against a registered list, never string-prefixed.
