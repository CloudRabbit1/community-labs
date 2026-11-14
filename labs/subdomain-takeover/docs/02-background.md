# Background

## DNS CNAME records

A CNAME (Canonical Name) record is a DNS alias. `assets.example.com CNAME example-company.netlify.app` means: resolve `assets.example.com` by looking up `example-company.netlify.app`. Browsers and HTTP clients follow this chain transparently.

## Dangling CNAMEs

When a company deletes their Netlify site but forgets to remove the DNS record, the CNAME still points to `example-company.netlify.app`. Anyone can register that Netlify site name. Once registered, DNS resolves `assets.example.com` to the attacker-controlled Netlify deployment.

## Why XSS is possible

A script loaded from `assets.example.com` runs in the security context of that origin. If a cookie is scoped to `.example.com` (the parent domain), it is accessible from any subdomain including `assets.example.com`. An attacker who controls the subdomain can serve JavaScript that reads `document.cookie` and exfiltrates session tokens to an external server.

## Common vulnerable providers

Subdomain takeover has been confirmed on Netlify, GitHub Pages, Heroku, AWS S3, Azure Blob Storage, and many other providers. The common thread is: provider lets anyone register a name, and DNS record stays after the account is deleted.
