# Background

## Content-Length vs Transfer-Encoding

`Content-Length` says the body is exactly N bytes:

```
POST / HTTP/1.1
Content-Length: 11

hello world
```

`Transfer-Encoding: chunked` sends the body in pieces, each preceded by its byte count in hex, terminated by a zero-length chunk:

```
POST / HTTP/1.1
Transfer-Encoding: chunked

5\r\n
hello\r\n
6\r\n
 world\r\n
0\r\n
\r\n
```

## What the RFC Says

RFC 7230 section 3.3.3 is explicit: if a request has both `Transfer-Encoding` and `Content-Length`, the `Transfer-Encoding` takes precedence. The server must ignore `Content-Length` and parse chunked TE. Any server that uses `Content-Length` when both headers are present is violating the spec.

## Why This Creates a Desync

A reverse proxy chain where the frontend uses CL and the backend uses TE:

1. Attacker sends a request with `Content-Length: X` and `Transfer-Encoding: chunked`.
2. Frontend reads X bytes of body and forwards the raw request to the backend.
3. Backend parses the chunked body and stops at `0\r\n\r\n`.
4. The bytes between the chunked terminator and the end of the CL-defined body are now "left over" in the backend's read buffer.
5. Those bytes become the prefix of the next HTTP request the backend processes.
6. The attacker controls what those bytes say.

## The Terminator

The chunked body terminator is `0\r\n\r\n`: a zero-length chunk (`0\r\n`) followed by an empty trailer section (`\r\n`). Everything after that terminator is not part of the chunked body. The backend sees it as the start of whatever comes next.
