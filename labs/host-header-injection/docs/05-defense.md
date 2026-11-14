# Defense

## The Root Cause

The application trusted attacker-supplied input (the `Host` header) when generating a URL that gets sent to a user. The fix is to never derive the application's own base URL from the request.

## Fix 1: Hardcode the Base URL

The simplest fix is to configure the application's base URL explicitly and never read the `Host` header for URL generation:

```python
# In app config
APP_BASE_URL = os.environ.get('APP_BASE_URL', 'http://localhost:8090')

# In the reset endpoint
reset_url = f"{APP_BASE_URL}/reset?token={token}"
```

This is the recommended approach. The base URL is a deployment-time concern, not a per-request one.

## Fix 2: Allowlist Trusted Hosts

If the application must support multiple hostnames, maintain an explicit allowlist:

```python
ALLOWED_HOSTS = {'app.example.com', 'www.example.com'}

host = request.headers.get('Host', '').split(':')[0]
if host not in ALLOWED_HOSTS:
    return jsonify({'error': 'Invalid Host header'}), 400
```

This prevents the attacker from injecting arbitrary domains while still supporting legitimate virtual hosting.

## Fix 3: Framework-Level Protection

Most web frameworks have built-in mechanisms. In Django, the `ALLOWED_HOSTS` setting rejects requests with unrecognized `Host` headers at the middleware layer. In Flask, `SERVER_NAME` can be set to restrict URL generation.

## What Does Not Work

Checking `request.host` in Python and comparing against a list in the endpoint is better than nothing, but the check must happen before the URL is generated. A common mistake is logging or saving the malformed URL before validating it.

## Checklist for Developers

- Never call `request.headers.get('Host')` to build redirect or reset URLs.
- Set `APP_BASE_URL` or equivalent as an environment variable at deploy time.
- Add an integration test that sends a forged `Host` header and asserts the generated URL does not contain it.
- Review all email-sending code paths for `Host` header references.
