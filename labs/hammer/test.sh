#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

BASE="http://localhost:8080"
EMAIL="admin@hammer.local"

# 1. Service is up
OUT=$(curl -sf "$BASE/")
if echo "$OUT" | grep -q "Hammer Auth"; then
  echo "[+] PASS: service up"
else
  echo "[-] FAIL: service not responding"; exit 1
fi

# 2. Request OTP
OUT=$(curl -sf -X POST "$BASE/forgot-password" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\"}")
if echo "$OUT" | grep -q "OTP"; then
  echo "[+] PASS: OTP requested"
else
  echo "[-] FAIL: forgot-password: $OUT"; exit 1
fi

# 3. Rate limit enforced without header rotation
BLOCKED=0
for i in $(seq 1 11); do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/reset-password" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"otp\":\"9999\"}")
  if [ "$CODE" = "429" ]; then
    BLOCKED=1; break
  fi
done
if [ "$BLOCKED" = "1" ]; then
  echo "[+] PASS: rate limit triggered"
else
  echo "[-] FAIL: rate limit never triggered"; exit 1
fi

# 4. Unauthenticated execute is rejected
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/execute" \
  -H "Content-Type: application/json" \
  -d '{"cmd":"id"}')
if [ "$CODE" = "401" ]; then
  echo "[+] PASS: execute requires auth"
else
  echo "[-] FAIL: unauthenticated execute returned $CODE"; exit 1
fi

# 5. Full exploit chain
OUT=$(python3 exploit/exploit.py "$BASE")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: exploit returned flag"
else
  echo "[-] FAIL: exploit output: $OUT"; exit 1
fi

echo "[+] All tests passed"
