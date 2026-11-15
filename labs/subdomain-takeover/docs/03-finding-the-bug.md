# Finding the Bug

## Step 1: Confirm the lab is running

```
curl -s http://127.0.0.1:8112/
```

You should see the DNS Subdomain Scanner home page.

## Step 2: Check for dangling CNAMEs

Query the DNS check endpoint for `assets.example.com`:

```
curl -s "http://127.0.0.1:8112/dns/check?domain=assets.example.com"
```

Expected response:

```json
{
  "domain": "assets.example.com",
  "cname": "example-company.netlify.app",
  "status": "DANGLING",
  "vulnerable": true,
  "flag1": "POC{...}"
}
```

The status is `DANGLING`: the CNAME target `example-company.netlify.app` no longer resolves to an active site.

## Step 3: Understand what DANGLING means

The company deleted their Netlify deployment but kept the DNS record. The name `example-company.netlify.app` is now available for registration. Anyone who registers it will control the content served at `assets.example.com`.

## Step 4: Verify the XSS endpoint is blocked before claiming

```
curl -si http://127.0.0.1:8112/xss-test
```

Expected response: `403 FORBIDDEN`. The subdomain has not been claimed yet.
