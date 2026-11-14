# Background

## The WebSocket Upgrade

A WebSocket connection starts as a normal HTTP request with two extra headers:

```
GET /chat HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
```

The server responds with `101 Switching Protocols`. After that, both sides agree to speak the WebSocket framing protocol instead of HTTP. Each message is wrapped in a WebSocket frame with a small header indicating length, opcode, and masking.

## What a Proxy Should Do

A correctly implemented WebSocket proxy should:
1. Forward the HTTP upgrade request to the backend.
2. Return the 101 response to the client.
3. Parse WebSocket frames in both directions and forward them as frames.

## What This Proxy Does

This proxy skips step 3. After the handshake, it opens two goroutine-style threads that copy raw bytes from one socket to the other without any parsing. Whatever the client sends goes straight to the backend as bytes.

## Why That Is a Problem

The backend is an HTTP server. It does not know about WebSocket frames. When it receives bytes after the upgrade, it tries to parse them as HTTP. If those bytes look like `GET /admin HTTP/1.1\r\n...`, the backend processes that request exactly as it would any other HTTP request.

The frontend has access controls for `/admin`. The backend does not, because the backend assumes it is only reachable from the proxy after a legitimate WebSocket session.
