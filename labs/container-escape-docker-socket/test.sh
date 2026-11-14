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
  curl -sf http://localhost:8080/health >/dev/null 2>&1 && break
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

echo "[*] Verifying SSRF is blocked without body..."
STATUS=$(curl -s -o /dev/null -w '%{http_code}' -X POST \
  -H "Content-Type: application/json" -d '{}' http://localhost:8080/fetch)
if [ "$STATUS" = "400" ]; then
  echo "[+] PASS: empty fetch rejected"
else
  echo "[-] FAIL: expected 400, got $STATUS"
  exit 1
fi

echo "[+] All tests passed"
