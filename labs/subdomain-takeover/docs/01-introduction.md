# Introduction

Subdomain takeover happens when a DNS record points to an external service that no longer exists. If an attacker registers that service, they control what content is served at the original subdomain, including JavaScript that runs in the context of the parent domain.

This lab simulates a company subdomain `assets.example.com` with a dangling CNAME pointing to a deleted Netlify site. You will discover the dangling record, claim the external service, and demonstrate XSS execution that steals an admin session cookie.

## What you will do

1. Identify a dangling CNAME using the DNS check tool.
2. Register the external service to claim the subdomain.
3. Trigger an XSS payload on the claimed subdomain to steal a victim cookie.

## Why it matters

A subdomain takeover allows an attacker to serve arbitrary content under a trusted domain. Because the payload runs on `assets.example.com`, it inherits the trust of that domain. It can steal cookies scoped to `.example.com`, make credentialed API requests, and bypass same-origin policy restrictions that would block a cross-origin attacker.
