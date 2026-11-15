# Defense

## Normalize at the Edge

The frontend should enforce a single body-length mechanism. When both `Content-Length` and `Transfer-Encoding` appear on the same request, the frontend has two options:
- Strip `Content-Length` and let the backend use chunked TE only.
- Reject the request with `400 Bad Request`.

RFC 7230 says the backend should do this too, but defense-in-depth means doing it at the proxy where you have more control.

## Use HTTP/2 on the Backend

HTTP/2 does not have the CL/TE ambiguity. It uses a framing layer that encodes request length explicitly. Upgrading the frontend-to-backend connection to HTTP/2 eliminates the parsing mismatch entirely.

## Disable HTTP Keep-Alive or Pipelining Between Proxy and Backend

Request smuggling requires the frontend and backend to share a persistent connection. If the frontend opens a new backend connection per request (no keep-alive), there is no shared buffer for smuggled bytes to poison.

## Revalidate Access Controls at the Backend

The backend should not assume that reaching it via the proxy implies authorization. Apply the same access controls at the backend that the frontend enforces. The frontend's 403 on `/admin` is a first line of defense, not the only one.
