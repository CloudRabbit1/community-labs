#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Normal GET returns service info without flag
OUT=$(curl -sf "http://localhost:8080/")
if echo "$OUT" | grep -qE 'POC\{'; then
  echo "[-] FAIL: flag returned on normal request"; exit 1
else
  echo "[+] PASS: normal GET returns service info"
fi

# 2. Direct /admin access is blocked on the frontend
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/admin")
if [ "$STATUS" = "403" ] || [ "$STATUS" = "404" ]; then
  echo "[+] PASS: /admin blocked on frontend (HTTP $STATUS)"
else
  echo "[-] FAIL: /admin not blocked (HTTP $STATUS)"; exit 1
fi

# 3. CL.TE smuggling exploit captures the flag
OUT=$(python3 exploit/exploit.py http://localhost:8080)
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: CL.TE smuggling captured flag"
else
  echo "[-] FAIL: $OUT"; exit 1
fi

echo "[+] All tests passed"
