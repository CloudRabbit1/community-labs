# Defense

## Parse WebSocket Frames

The proxy must parse the WebSocket framing protocol instead of copying raw bytes. A WebSocket frame starts with a 2-byte header containing the opcode, payload length, and masking flag. The proxy should decode each frame, validate the opcode, and re-encode it before forwarding.

If the bytes after the handshake do not conform to the WebSocket frame format, the proxy should close the connection with status code 1002 (Protocol Error).

## Enforce the Protocol Upgrade at the Backend

The backend should not process data as HTTP after agreeing to a WebSocket upgrade. Once a connection has sent `101 Switching Protocols`, the connection is a WebSocket connection. Any subsequent data that looks like HTTP should be rejected, not processed.

## Use a Validated Proxy Library

Do not write WebSocket proxying from scratch. Libraries that implement RFC 6455 handle frame parsing, masking validation, ping/pong, and protocol error handling. Rolling your own risks exactly the kind of oversight demonstrated here.

## Defense in Depth at the Backend

The backend should not assume that reaching it via WebSocket implies authorization. Apply the same access controls at the backend that the frontend enforces. The frontend's 403 on `/admin` is a first line of defense, not the only one.
