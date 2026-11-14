#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Service health
OUT=$(curl -sf "http://localhost:8080/")
if echo "$OUT" | grep -q "NoteKeeper"; then
  echo "[+] PASS: service is up"
else
  echo "[-] FAIL: service not responding"; exit 1
fi

# 2. /admin without session returns 401
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/admin")
if [ "$STATUS" = "401" ]; then
  echo "[+] PASS: /admin returns 401 without session"
else
  echo "[-] FAIL: expected 401, got $STATUS"; exit 1
fi

# 3. Normal user gets 403 on /admin
COOKIE=$(curl -s -X POST http://localhost:8080/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"testuser","password":"pass123"}' \
  -D - | grep -i set-cookie | grep session | sed 's/.*session=\([^;]*\).*/\1/')
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/admin" \
  -H "Cookie: session=$COOKIE")
if [ "$STATUS" = "403" ]; then
  echo "[+] PASS: normal user gets 403 on /admin"
else
  echo "[-] FAIL: expected 403, got $STATUS"; exit 1
fi

# 4. Full exploit: predict session_1 and get flag
OUT=$(python3 exploit/exploit.py http://localhost:8080)
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: exploit retrieved flag"
else
  echo "[-] FAIL: exploit output: $OUT"; exit 1
fi

echo "[+] All tests passed"
