# Defense

## Remove DNS records before deleting services

The root cause is a DNS record that outlived the service it pointed to. The fix is a process change: before deleting any hosted service (Netlify site, GitHub Pages repo, Heroku app, S3 bucket), remove the corresponding DNS records first.

If the order is reversed and the service is deleted first, the window between deletion and DNS record removal is a live vulnerability.

## Audit existing DNS records

Scan all CNAME records in your DNS zone and verify that each target still resolves to an active, owned service. Tools like `subjack`, `nuclei` with DNS templates, or `dnsreaper` can automate this across large subdomain sets.

## Monitor for unauthorized registrations

For high-value domains, use DNS monitoring services that alert when a previously NXDOMAIN CNAME target becomes resolvable. If `example-company.netlify.app` goes from NXDOMAIN to answering, that is a takeover signal.

## Scope cookies carefully

Set session cookies with the most restrictive domain possible. A cookie scoped to `app.example.com` rather than `.example.com` cannot be read by other subdomains. This limits the blast radius of a takeover even if one subdomain is compromised.
