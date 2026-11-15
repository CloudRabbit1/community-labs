# Background

## What middleware does

Middleware sits between the client and the route handler. Every request passes through it first. A middleware function can inspect the request, modify headers, check a session cookie, and either pass the request forward or return a response immediately.

In Next.js, middleware runs at the edge before any route handler. It is the right place to enforce authentication because it runs first, before the route can expose any data.

## How internal headers work

When a framework processes a request internally (for example, redirecting one route to another, or passing a request through a sub-request pipeline), it sometimes needs to mark the request so downstream handlers know it has already been processed. One way to do this is a special header that only internal code sets.

The problem: HTTP headers are not signed. Any client can set any header. If the framework trusts an internal header without verifying it came from an internal source, an external attacker can forge it.

## CVE-2025-29927

Next.js used `x-middleware-subrequest` to signal that a request had already run through middleware. The middleware code checked for this header and, if present, skipped processing. This was intended for internal sub-requests, but the check did not distinguish between internal and external origins. Sending `x-middleware-subrequest: middleware` from a browser or curl bypassed any middleware-based auth check entirely.

The fix was to strip the header from incoming external requests before middleware ran.
