# Defense

## Strip internal headers at the edge

The fix for CVE-2025-29927 was to remove `x-middleware-subrequest` from every incoming external request before the middleware chain ran. Internal code could still set it, but no external client could pass it through.

In a real Next.js deployment: upgrade to a patched version (15.2.3+ / 14.2.25+ / 13.5.9+). The framework now strips the header automatically.

For any framework using internal trust headers: strip them in the outermost layer (reverse proxy, load balancer, or edge function) before they reach application code.

## Do not trust headers for auth decisions

Internal headers are meant for internal communication. Using them to signal auth state assumes the value cannot be forged. HTTP headers carry no such guarantee. Session state should live in a signed, server-issued token (cookie with HMAC or JWT), not in a header the client controls.

## Defense in depth

Even if middleware is bypassed, route handlers should not unconditionally trust that auth was already checked. Each handler can re-verify the session independently. This limits the blast radius of a middleware bypass: reaching the route is not enough if the handler also checks credentials.
