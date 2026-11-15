# Defense

## Fix 1: Never Use Unvalidated Headers to Build URLs

The simplest fix: configure the application's base URL explicitly and ignore `X-Forwarded-Host` for URL generation.

```python
APP_HOST = os.environ.get('APP_HOST', 'localhost:8094')

# In the endpoint:
script_src = f'http://{APP_HOST}/static/app.js'
```

If you need to trust `X-Forwarded-Host` from an upstream reverse proxy, validate it against an allowlist:

```python
ALLOWED_HOSTS = {'app.example.com', 'www.example.com'}

forwarded_host = request.headers.get('X-Forwarded-Host', '')
if forwarded_host not in ALLOWED_HOSTS:
    forwarded_host = request.host
```

## Fix 2: Add Reflected Headers to the Cache Key

If the application legitimately varies its response based on a header (e.g., language, encoding), that header must be in the cache key:

```python
# Cache key includes the header
cache_key = f'GET:/home:{request.headers.get("X-Forwarded-Host", "")}'
```

This prevents poisoning because a request with `X-Forwarded-Host: attacker.com` gets its own cache slot and cannot contaminate requests without the header.

## Fix 3: Strip Unrecognized Forwarding Headers at the Edge

Configure your CDN or reverse proxy (Nginx, Cloudflare, Varnish) to strip `X-Forwarded-Host` from incoming requests before they reach the origin server. Only your own proxy should set this header.

Nginx example:

```nginx
proxy_set_header X-Forwarded-Host $host;  # always overwrite
```

## Fix 4: Set Cache-Control: no-store on Dynamic Responses

If a response is personalized or uses request headers for content, it should not be cached at all:

```python
response.headers['Cache-Control'] = 'no-store, private'
```

## Checklist for Developers

- Audit every header the application reads for URL construction, redirect targets, or link generation.
- For each such header: either validate against an allowlist or add it to the cache key.
- Never let a CDN or in-process cache store a response without reviewing what inputs affect the response body.
- Run Burp Suite's param miner or similar tools to discover unkeyed header reflection automatically.
