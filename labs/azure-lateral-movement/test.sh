#!/usr/bin/env bash
set -e

DC="docker compose"
command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1 && DC="docker-compose"

PORT=8080
FAIL=0

cleanup() { $DC down --remove-orphans 2>/dev/null || true; }
trap cleanup EXIT

echo "[*] Building container..."
$DC up --build -d

echo "[*] Waiting for lab on port $PORT..."
for i in $(seq 1 30); do
    curl -sf "http://127.0.0.1:$PORT/" >/dev/null 2>&1 && { echo "[+] Lab up"; break; }
    sleep 2
    [ "$i" -eq 30 ] && { echo "[FAIL] Lab did not come up"; $DC logs; exit 1; }
done

echo ""
echo "[*] Running three-hop exploit..."
OUTPUT=$(python3 exploit/exploit.py "http://127.0.0.1:$PORT" 2>&1)
echo "$OUTPUT"

if echo "$OUTPUT" | grep -qE 'POC\{[0-9a-f]+\}'; then
    echo "[PASS] Flag recovered via hop chain"
else
    echo "[FAIL] Flag not found"
    FAIL=1
fi

echo ""
echo "[*] Confirm IMDS requires Metadata header..."
REJECT=$(curl -s "http://127.0.0.1:$PORT/metadata/identity/oauth2/token?resource=https://vault.azure.net" 2>&1 || true)
if echo "$REJECT" | grep -qi "missing"; then
    echo "[PASS] IMDS correctly rejects requests without Metadata header"
else
    echo "[FAIL] IMDS did not enforce Metadata header"
    FAIL=1
fi

echo ""
[ "$FAIL" -eq 0 ] && echo "[PASS] All tests passed" && exit 0
echo "[FAIL] One or more tests failed"; exit 1
