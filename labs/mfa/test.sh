#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Service health check
OUT=$(curl -sf "http://localhost:8080/")
if echo "$OUT" | grep -q "SecureBank"; then
  echo "[+] PASS: service is up"
else
  echo "[-] FAIL: service not responding"; exit 1
fi

# 2. /flag without session should return 401
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/flag")
if [ "$STATUS" = "401" ]; then
  echo "[+] PASS: /flag returns 401 without session"
else
  echo "[-] FAIL: expected 401, got $STATUS"; exit 1
fi

# 3. Full exploit: predict OTP and retrieve flag
OUT=$(python3 exploit/exploit.py http://localhost:8080)
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: exploit retrieved flag"
else
  echo "[-] FAIL: exploit output: $OUT"; exit 1
fi

echo "[+] All tests passed"
