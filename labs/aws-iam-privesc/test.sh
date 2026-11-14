#!/usr/bin/env bash
set -euo pipefail

DC="docker compose"
command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1 && DC="docker-compose"

cd "$(dirname "$0")"

echo "[*] Building and starting lab..."
$DC up --build -d

cleanup() { $DC down -v 2>/dev/null || true; }
trap cleanup EXIT

echo "[*] Waiting for service..."
for i in $(seq 1 30); do
  curl -sf -H "X-Access-Key: AKIAI-DEV-USER-KEY" http://localhost:8080/ >/dev/null 2>&1 && break
  sleep 1
done

echo "[*] Running exploit..."
OUT=$(python3 exploit/exploit.py http://localhost:8080)
echo "$OUT"

if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: flag captured"
else
  echo "[-] FAIL: flag not found in exploit output"
  exit 1
fi

echo "[*] Verifying auth enforcement..."
STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/)
if [ "$STATUS" = "401" ]; then
  echo "[+] PASS: unauthenticated request rejected"
else
  echo "[-] FAIL: expected 401 without auth, got $STATUS"
  exit 1
fi

echo "[+] All tests passed"
