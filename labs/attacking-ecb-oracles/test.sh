#!/usr/bin/env bash
# End-to-end test for attacking-ecb-oracles.
# Builds the oracle, runs the byte-at-a-time exploit, asserts the flag, tears down.
set -e

DC="docker compose"
command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1 && DC="docker-compose"

PORT=5000
FAIL=0

cleanup() {
    $DC down --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

echo "[*] Building container..."
$DC up --build -d

echo "[*] Waiting for oracle on port $PORT..."
for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:$PORT/encrypt?input=test" >/dev/null 2>&1; then
        echo "[+] Oracle up"
        break
    fi
    sleep 2
    if [ "$i" -eq 30 ]; then
        echo "[FAIL] Oracle did not come up"
        $DC logs
        exit 1
    fi
done

echo ""
echo "[*] Running byte-at-a-time exploit..."
OUTPUT=$(python3 exploit/exploit.py "http://127.0.0.1:$PORT" 2>&1)
echo "$OUTPUT"

if echo "$OUTPUT" | grep -qE 'POC\{[0-9a-f]+\}'; then
    echo "[PASS] Flag recovered"
else
    echo "[FAIL] Flag not found in exploit output"
    FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
    echo "[PASS] All tests passed"
    exit 0
else
    echo "[FAIL] One or more tests failed"
    exit 1
fi
