#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")
$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Login and capture session cookie
COOKIE_JAR=$(mktemp)
curl -sf -c "$COOKIE_JAR" -X POST http://localhost:8080/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}' > /dev/null
grep -q "session" "$COOKIE_JAR" && echo "[+] PASS: login sets session cookie" || { echo "[-] FAIL: no session cookie"; exit 1; }

# 2. Access profile without Origin: returns flag
OUT=$(curl -sf -b "$COOKIE_JAR" http://localhost:8080/api/profile)
echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}' && echo "[+] PASS: profile returns flag" || { echo "[-] FAIL: $OUT"; exit 1; }

# 3. Access profile with attacker Origin: CORS reflects it, flag still readable
OUT2=$(curl -sf -b "$COOKIE_JAR" -H 'Origin: https://evil.com' http://localhost:8080/api/profile)
echo "$OUT2" | grep -qE 'POC\{[0-9a-f]{32}\}' && echo "[+] PASS: attacker origin can read flag (CORS reflected)" || { echo "[-] FAIL: $OUT2"; exit 1; }

# 4. Preflight reflects evil.com origin
PREFLIGHT=$(curl -sI -X OPTIONS http://localhost:8080/api/profile -H 'Origin: https://evil.com' -H 'Access-Control-Request-Method: GET')
echo "$PREFLIGHT" | grep -qi "access-control-allow-origin: https://evil.com" && echo "[+] PASS: preflight reflects attacker origin" || { echo "[-] FAIL preflight: $PREFLIGHT"; exit 1; }

# 5. No cookie: 401
STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/profile)
[ "$STATUS" = "401" ] && echo "[+] PASS: unauthenticated request blocked" || { echo "[-] FAIL: expected 401 got $STATUS"; exit 1; }

rm -f "$COOKIE_JAR"
echo "[+] All tests passed"
