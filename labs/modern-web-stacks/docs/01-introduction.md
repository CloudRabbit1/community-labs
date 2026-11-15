# Introduction

Modern web frameworks route every incoming request through a middleware chain before it reaches the application logic. Middleware handles cross-cutting concerns: logging, rate limiting, session validation, authentication. If middleware decides a request is authorized, it passes it along. If not, it short-circuits with a 401 or redirect.

This model is powerful, but it introduces a trust assumption: middleware only works as a gate if nothing can bypass it.

CVE-2025-29927 showed that Next.js had exactly this problem. The framework used an internal header, `x-middleware-subrequest`, to mark requests that had already passed through the middleware chain. If that header was present, the middleware stepped aside. An attacker could forge the header on any external request and reach any middleware-protected route without credentials.

This lab reproduces that pattern. The goal is to access `/admin` without a valid session by understanding how the middleware trust mechanism works.
