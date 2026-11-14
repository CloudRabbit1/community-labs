#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Authorize with legitimate redirect_uri works
OUT=$(curl -sf -X POST -H 'Content-Type: application/json' \
  -d '{"client_id":"app","redirect_uri":"http://localhost:8080/callback","state":"s1","allow":true}' \
  "http://localhost:8080/oauth/authorize")
if echo "$OUT" | grep -q '"code"'; then
  echo "[+] PASS: authorize with registered redirect_uri returns code"
else
  echo "[-] FAIL: $OUT"; exit 1
fi

# 2. Authorize with attacker redirect_uri also works (the vulnerability)
OUT=$(curl -sf -X POST -H 'Content-Type: application/json' \
  -d '{"client_id":"app","redirect_uri":"http://attacker.example.com/steal","state":"s2","allow":true}' \
  "http://localhost:8080/oauth/authorize")
if echo "$OUT" | grep -q '"code"' && echo "$OUT" | grep -q 'attacker.example.com'; then
  echo "[+] PASS: attacker redirect_uri accepted (vulnerability confirmed)"
else
  echo "[-] FAIL: $OUT"; exit 1
fi

# 3. Full exploit: code stolen via open redirect, token obtained, flag captured
OUT=$(python3 exploit/exploit.py http://localhost:8080 2>&1) || true
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: exploit captured flag via open redirect"
else
  echo "[-] FAIL: $OUT"; exit 1
fi

echo "[+] All tests passed"
