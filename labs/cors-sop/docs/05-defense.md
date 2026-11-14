# Defense

The fix is an explicit allowlist. Replace the origin reflection with a comparison:

```python
ALLOWED_ORIGINS = {"https://app.corp.com", "https://www.corp.com"}

def cors_headers(self) -> dict:
    origin = self.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",
        }
    return {}
```

If the origin is not in the list, the server returns no CORS headers. The browser then refuses to expose the response body to the calling page.

For APIs that do not need credentials, use `Access-Control-Allow-Origin: *` without `Access-Control-Allow-Credentials`. The wildcard is safe when cookies are not involved.

For APIs that serve different data to different users, the allowlist is the only correct approach. Dynamic origin validation using regex or substring matching is dangerous. The pattern `.*\.corp\.com` matches `evil-corp.com`. The pattern `corp\.com` matches `notcorp.com`. Use exact string comparison against a set, not pattern matching.

Detection: check your server's access logs for unusual `Origin` headers. Any origin you do not recognise that is getting back successful CORS responses is a misconfiguration.
