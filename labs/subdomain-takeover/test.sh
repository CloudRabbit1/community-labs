#!/usr/bin/env bash
# Subdomain takeover via dangling CNAME end-to-end test
set -e

DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")
PORT=8112
BASE="http://127.0.0.1:$PORT"
FAIL=0

cleanup() {
  $DC down --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

echo "[*] Building container..."
$DC up --build -d

echo "[*] Waiting for Flask on port $PORT..."
for i in $(seq 1 30); do
  curl -sf "$BASE/" >/dev/null 2>&1 && break
  sleep 2
  if [ "$i" -eq 30 ]; then echo "[FAIL] Service timed out"; $DC logs; exit 1; fi
done
echo "[*] Service ready"

# --- Test 1: home page ---
echo ""
echo "[*] Test 1: home page"
OUT=$(curl -sf "$BASE/")
if echo "$OUT" | grep -qi "DNS"; then
  echo "[PASS] Home page contains DNS"
else
  echo "[FAIL] Home page missing DNS"; FAIL=1
fi

# --- Test 2: DNS check returns DANGLING and flag1 ---
echo ""
echo "[*] Test 2: DNS check finds dangling CNAME and returns flag1"
OUT=$(curl -sf "$BASE/dns/check?domain=assets.example.com")
if echo "$OUT" | grep -q "DANGLING" && echo "$OUT" | grep -qE '"POC\{[0-9a-f]+\}"'; then
  echo "[PASS] DNS check returned DANGLING status and flag1"
else
  echo "[FAIL] DNS check did not return expected output: $OUT"; FAIL=1
fi

# --- Test 3: claim with wrong name returns 400 ---
echo ""
echo "[*] Test 3: claiming wrong site returns 400"
STATUS=$(curl -so /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
  -d '{"site_name":"wrong-site.netlify.app"}' "$BASE/claim")
if [ "$STATUS" = "400" ]; then
  echo "[PASS] Wrong claim returns 400"
else
  echo "[FAIL] Expected 400, got $STATUS"; FAIL=1
fi

# --- Test 4: claim then xss-test returns flag2 ---
echo ""
echo "[*] Test 4: claim subdomain then trigger XSS for flag2"
curl -sf -X POST -H 'Content-Type: application/json' \
  -d '{"site_name":"example-company.netlify.app"}' "$BASE/claim" >/dev/null
OUT=$(curl -sf "$BASE/xss-test")
if echo "$OUT" | grep -qE '"POC\{[0-9a-f]+\}"'; then
  echo "[PASS] XSS test returned flag2"
else
  echo "[FAIL] XSS test did not return flag2: $OUT"; FAIL=1
fi

# --- Test 5: automated exploit ---
echo ""
echo "[*] Test 5: automated exploit"
EXPLOIT_OUT=$(python3 exploit/exploit.py "$BASE" 2>&1)
echo "$EXPLOIT_OUT"
FLAG_COUNT=$(echo "$EXPLOIT_OUT" | grep -cE 'POC\{[0-9a-f]+\}' || true)
if [ "$FLAG_COUNT" -ge 2 ]; then
  echo "[PASS] Exploit returned both flags"
else
  echo "[FAIL] Exploit did not return 2 POC flags"; FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[PASS] All tests passed"; exit 0
else
  echo "[FAIL] One or more tests failed"; exit 1
fi
