#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Service responds
OUT=$(curl -sf "http://localhost:8080/")
if echo "$OUT" | grep -q "MatryoshkaMonitor"; then
  echo "[+] PASS: service is up"
else
  echo "[-] FAIL: service not responding"; exit 1
fi

# 2. Direct flag read is blocked before escape
OUT=$(curl -sf "http://localhost:8080/execute?cmd=cat+/flag.txt")
if echo "$OUT" | grep -q "Permission denied"; then
  echo "[+] PASS: direct flag read blocked before escape"
else
  echo "[-] FAIL: flag returned without completing escape sequence"; exit 1
fi

# 3. Full escape sequence via exploit.py
OUT=$(python3 exploit/exploit.py http://localhost:8080)
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: escape sequence returned flag"
else
  echo "[-] FAIL (exploit): $OUT"; exit 1
fi

echo "[+] All tests passed"
