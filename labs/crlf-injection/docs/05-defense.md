# 05: Defense

## The fix: strip CR and LF before writing headers

The one-line fix is to remove `\r` and `\n` from any user-supplied value before it goes into a header:

```python
safe_url = url.replace('\r', '').replace('\n', '')
self.send_header('Location', safe_url)
```

The lab's `/safe-redirect` endpoint demonstrates this. The same payload that injects a header on `/redirect` produces a harmless single-line Location value on `/safe-redirect`.

## Use a framework with built-in sanitization

Flask, Django, and most other Python web frameworks sanitize header values automatically. Flask's Werkzeug raises a `ValueError` or silently strips newlines when you try to set a header containing `\r` or `\n`. If you are writing a redirect handler in Flask:

```python
from flask import Flask, redirect, request

app = Flask(__name__)

@app.get('/redirect')
def redir():
    url = request.args.get('url', '/')
    return redirect(url)  # Werkzeug sanitizes automatically
```

The vulnerability only appears when using Python's stdlib `http.server` directly, writing to raw sockets, or other low-level HTTP implementations that do not sanitize.

## Validate the redirect destination

Even after stripping CRLF, open redirects to attacker-controlled domains are dangerous. A complete fix restricts the redirect target to a safe allowlist:

```python
ALLOWED_PATHS = {'/home', '/dashboard', '/profile'}

def safe_redirect(url: str) -> str:
    # strip CRLF
    url = url.replace('\r', '').replace('\n', '')
    # only redirect to known paths
    if url not in ALLOWED_PATHS:
        url = '/home'
    return url
```

## Security scanner detection

Most web application scanners (Burp Suite, OWASP ZAP) include CRLF injection checks. They send payloads like `%0D%0AX-Scanner-Test: 1` in common parameters and inspect responses for injected headers. Running a scanner against any redirect endpoint is a good first check.
