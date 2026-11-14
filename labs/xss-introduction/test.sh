#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Board starts empty
OUT=$(curl -sf "http://localhost:8080/api/comments")
COUNT=$(echo "$OUT" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])")
if [ "$COUNT" -eq 0 ]; then
  echo "[+] PASS: board starts empty"
else
  echo "[-] FAIL: expected 0 comments, got $COUNT"; exit 1
fi

# 2. /stolen returns null before any payload
OUT=$(curl -sf "http://localhost:8080/stolen")
COOKIE=$(echo "$OUT" | python3 -c "import sys,json; print(json.load(sys.stdin)['cookie'])")
if [ "$COOKIE" = "None" ]; then
  echo "[+] PASS: /stolen returns null before attack"
else
  echo "[-] FAIL: unexpected cookie before attack: $COOKIE"; exit 1
fi

# 3. Full exploit run
OUT=$(python3 exploit/exploit.py http://localhost:8080)
echo "$OUT"
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: exploit captured flag"
else
  echo "[-] FAIL: flag not found in exploit output"; exit 1
fi

echo "[+] All tests passed"
