# Introduction

## What This Lab Is About

Web cache poisoning is an attack where an attacker tricks a cache into storing a malicious response and serving it to other users. The attacker sends one crafted request; every victim who requests the same URL afterwards gets the poisoned response without knowing it.

The prerequisite is an HTTP header that the application uses to build its response but that the cache does not include in the cache key. Such a header is called unkeyed. An attacker can set it to anything, and the cache will serve their response as if it were the canonical one for that URL.

## The Vulnerable Pattern

The `/home` endpoint reads `X-Forwarded-Host` to build script URLs:

```python
forwarded_host = request.headers.get('X-Forwarded-Host', request.host)
body = {
    'script_src': f'http://{forwarded_host}/static/app.js',
    ...
}
```

The cache stores the response keyed on `GET:/home` -- the path only. It ignores `X-Forwarded-Host`.

An attacker who sends `X-Forwarded-Host: attacker.com` causes the cache to store:

```json
{"script_src": "http://attacker.com/static/app.js", ...}
```

Every subsequent request to `/home` hits the cache and receives the attacker's URL in `script_src`.

## Real-World Impact

In a browser-based application, `script_src` would be a `<script src="...">` tag. The victim's browser loads and executes a script from `attacker.com`. This is reflected XSS delivered via cache poisoning -- it persists until the cache expires and can affect every visitor to the site.
