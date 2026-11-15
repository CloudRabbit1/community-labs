# Background

## How Web Caches Work

A web cache (CDN, reverse proxy, or in-process cache) stores HTTP responses and serves them to multiple clients. The cache key is what determines whether a request is a hit or a miss. Requests that produce the same cache key get the same cached response.

The simplest cache key is the URL path. Many caches also include the query string, the `Accept` header for content negotiation, and the cookie for personalized content.

## Keyed vs Unkeyed Inputs

An input is keyed if it is part of the cache key. An input is unkeyed if the cache ignores it even though the application uses it.

| Input | Typically Keyed? |
|-------|------------------|
| URL path | Yes |
| Query string | Yes |
| Cookie | Sometimes |
| `X-Forwarded-Host` | Rarely |
| `X-Original-URL` | Rarely |
| `Accept-Language` | Rarely |

When an application uses an unkeyed header to build the response, an attacker can inject it, poison the cache, and affect all users of that cache entry.

## The Attack Flow

1. Attacker sends `GET /page HTTP/1.1\r\nX-Forwarded-Host: attacker.com`
2. Cache checks key `GET:/page` -- miss.
3. Application processes the request, reads `X-Forwarded-Host: attacker.com`, builds response with `attacker.com` in body.
4. Cache stores that response under key `GET:/page`.
5. Victim sends `GET /page HTTP/1.1` (no `X-Forwarded-Host`).
6. Cache checks key `GET:/page` -- hit. Serves poisoned response.
7. Victim's browser loads `http://attacker.com/static/app.js`.

Steps 5-7 repeat for every visitor until the cache entry expires.

## Why X-Forwarded-Host Exists

`X-Forwarded-Host` is a standard header set by reverse proxies to tell the upstream application what domain the original client requested. Applications use it to build absolute URLs in responses. The header is legitimate but must be validated against an allowlist of known domains before being used.
