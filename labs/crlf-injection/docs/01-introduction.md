# 01: Introduction

This lab demonstrates CRLF injection, a vulnerability where an attacker inserts carriage return (`\r`, byte 0x0D) and line feed (`\n`, byte 0x0A) characters into an HTTP header value to inject extra headers into the server's response.

## The scenario

CorpRedirector is a small internal service that bounces users to other URLs. It accepts the destination as a query parameter and sets the HTTP `Location` header:

```
GET /redirect?url=/home HTTP/1.1
...

HTTP/1.1 302 Found
Location: /home
```

The developer never considered that the `url` parameter might contain newlines.

## Why it matters

An HTTP response header block looks like this:

```
HTTP/1.1 302 Found\r\n
Location: /home\r\n
Server: CorpRedirector\r\n
\r\n
```

Headers are separated by `\r\n`. If the attacker controls part of a header value and can embed `\r\n`, they can inject a new header entirely. For example, if the `Location` value is `/home\r\nSet-Cookie: session=evil`, the browser receives:

```
HTTP/1.1 302 Found\r\n
Location: /home\r\n
Set-Cookie: session=evil\r\n
\r\n
```

The browser sets the cookie. The attacker never touched the server's cookie logic.

## Real-world impact

CRLF injection in redirect headers has been used to:

- Set attacker-controlled session cookies (session fixation)
- Inject `X-Forwarded-For` or `X-Real-IP` to bypass IP-based access controls
- Inject `Content-Length: 0` to truncate response bodies
- Inject `Cache-Control: public` to force caching of private responses

Modern web frameworks (Flask, Django, Rails) sanitize header values before writing them. Bare socket servers and some legacy CGI environments do not.
