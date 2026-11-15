# 02: Background

## HTTP header format

Every HTTP response starts with a status line, followed by headers, followed by a blank line, followed by the body:

```
HTTP/1.1 302 Found\r\n
Location: /home\r\n
Content-Length: 0\r\n
\r\n
```

The `\r\n` (CRLF) sequence is the separator defined in RFC 7230. Parsers split on these two bytes to find where one header ends and the next begins.

## Why percent-encoding matters

Browsers and HTTP clients percent-encode characters that are not safe in URLs. The CRLF pair becomes `%0D%0A`:

- `%0D` is `\r` (carriage return, 0x0D)
- `%0A` is `\n` (line feed, 0x0A)

When the server receives the query string and decodes it, it gets back raw `\r\n` bytes. If those bytes end up inside a `Location` header value that is written to the socket without sanitization, the response is split.

## Why stdlib `http.server` is vulnerable

Python's `BaseHTTPRequestHandler.send_header(name, value)` writes this to the socket:

```python
self._headers_buffer.append(
    ("%s: %s\r\n" % (keyword, value)).encode("latin-1", "strict")
)
```

No newline stripping happens. If `value` contains `\r\n`, the response header block is split at that point.

Flask's `Werkzeug` library does sanitize. Its `Headers` object raises or strips newlines from header values. This is why the same vulnerability cannot be demonstrated in a Flask app without working around Werkzeug.

## URL encoding in practice

Python's `urllib.parse.quote` encodes unsafe characters:

```python
>>> import urllib.parse
>>> urllib.parse.quote('/safe\r\nX-Injected: hacked')
'/safe%0D%0AX-Injected%3A%20hacked'
```

Send that as the `url` parameter. The server decodes it with `unquote_plus`, gets `/safe\r\nX-Injected: hacked`, and writes it straight into the Location header.
