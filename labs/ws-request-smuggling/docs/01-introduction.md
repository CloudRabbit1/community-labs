# Introduction

WebSocket request smuggling exploits a gap between how a WebSocket proxy handles the upgrade handshake and what it does with the bytes that follow.

The proxy's job is to upgrade an HTTP connection to a persistent bidirectional channel. After the 101 handshake, the proxy starts forwarding bytes. If the proxy forwards those bytes without parsing WebSocket frames, an attacker can send a raw HTTP request through the tunnel instead of a WebSocket frame. The backend, which only understands HTTP, receives those bytes and processes them as a new HTTP request.

The result: the attacker reaches backend endpoints that the frontend proxy was supposed to protect.
