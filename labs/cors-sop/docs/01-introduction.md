# Introduction

Browsers enforce the Same-Origin Policy: a page on `evil.com` cannot read responses from `api.corp.com`. Cross-Origin Resource Sharing (CORS) is the mechanism that lets servers selectively relax that rule. This lab shows what happens when a server relaxes it for everyone without meaning to, by reflecting whatever `Origin` header the browser sends back in `Access-Control-Allow-Origin`. Combined with `Access-Control-Allow-Credentials: true`, any website on the internet can make authenticated requests to the API and read the response.

## What you will do

- Confirm the misconfiguration by sending a preflight request with an arbitrary origin and reading the reflected header
- Read the authenticated `/api/profile` endpoint from a cross-origin context using a session cookie
- Fix the bug by replacing origin reflection with an allowlist

## What you need

- Docker with Compose installed ([instructions in the README](../README.md))
- Basic comfort with curl
- Familiarity with HTTP headers
