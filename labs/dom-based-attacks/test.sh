#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. XSS sink: payload appears unescaped in innerHTML
OUT=$(curl -sf "http://localhost:8080/reflect?q=%3Cimg%20src%3Dx%20onerror%3Dalert%281%29%3E")
if echo "$OUT" | grep -qF '<img src=x onerror=alert(1)>'; then
  echo "[+] PASS: payload unescaped in innerHTML sink"
else
  echo "[-] FAIL: payload was escaped or missing"; exit 1
fi

# 2. Unauthenticated flag access returns 401
CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/api/flag")
if [ "$CODE" = "401" ]; then
  echo "[+] PASS: unauthenticated request blocked (401)"
else
  echo "[-] FAIL: expected 401, got $CODE"; exit 1
fi

# 3. Full exploit: login, fetch flag with session cookie
OUT=$(python3 exploit/exploit.py http://localhost:8080 2>&1) || true
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: exploit captured flag via DOM XSS session"
else
  echo "[-] FAIL: $OUT"; exit 1
fi

echo "[+] All tests passed"
