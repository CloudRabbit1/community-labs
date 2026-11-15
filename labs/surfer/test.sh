#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

BASE="http://localhost:8080"

# 1. Service is up
OUT=$(curl -sf "$BASE/")
if echo "$OUT" | grep -q "URL Preview Service"; then
  echo "[+] PASS: service up"
else
  echo "[-] FAIL: service not responding"; exit 1
fi

# 2. /fetch with missing url returns 400
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/fetch")
if [ "$CODE" = "400" ]; then
  echo "[+] PASS: missing url returns 400"
else
  echo "[-] FAIL: missing url returned $CODE"; exit 1
fi

# 3. SSRF exploit returns flag
OUT=$(python3 exploit/exploit.py "$BASE")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: SSRF returned flag from internal admin"
else
  echo "[-] FAIL: exploit output: $OUT"; exit 1
fi

echo "[+] All tests passed"
