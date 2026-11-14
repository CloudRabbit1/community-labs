#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down -v 2>/dev/null || true
$DC up --build -d
trap "$DC down -v" EXIT
sleep 5

# 1. Service is up
OUT=$(curl -sf "http://localhost:8080/")
echo "$OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'Docker' in d.get('service',''), d" 2>/dev/null
echo "[+] PASS: service is up"

# 2. Docker API accessible via proxy
OUT=$(curl -sf "http://localhost:8080/api/docker/containers/json")
echo "[+] PASS: Docker API accessible (containers/json returned)"

# 3. Full exploit run
OUT=$(python3 exploit/exploit.py http://localhost:8080)
echo "$OUT"
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: escape successful, flag captured"
else
  echo "[-] FAIL: flag not found in exploit output"; exit 1
fi

# Cleanup any escape containers the exploit created (they hold the volume)
docker ps -aq --filter volume=docker-rodeo-vault | xargs -r docker rm -f 2>/dev/null || true

echo "[+] All tests passed"
