#!/bin/sh
set -e

# --- Optional: assert the vulnerable condition at build time ---
# Fail the build here if the lab's core premise doesn't hold,
# so a package update doesn't silently break the lab.
# Example:
#   if ldd "$(which sshd)" 2>/dev/null | grep -qi pam; then
#       echo "FATAL: sshd links against PAM - this lab requires PAM-free" >&2
#       exit 1
#   fi

# --- Create accounts ---
# Every SSH lab needs at least one account with a real $6$ hash
# for OpenSSH's crypt() to have a valid salt to borrow. labadmin
# fills that role. Its password is irrelevant to the attack.
adduser -D labadmin
echo "labadmin:$(head -c 18 /dev/urandom | base64)" | chpasswd

# Target accounts - give them /bin/sh so the student lands somewhere useful.
adduser -D -s /bin/sh user1
adduser -D -s /bin/sh user2

# Lock with * not !
# ! causes OpenSSH to refuse before crypt() runs.
# * passes through to the crypt() comparison.
usermod -p '*' user1
usermod -p '*' user2

# --- Verify shadow entries ---
for account in user1 user2; do
    field=$(grep "^${account}:" /etc/shadow | cut -d: -f2)
    if [ "$field" != "*" ]; then
        echo "FATAL: ${account} shadow field is '${field}', expected '*'" >&2
        exit 1
    fi
done

# --- Generate flags (unique per container start) ---
FLAG1="LAB{$(head -c 12 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)}"
FLAG2="LAB{$(head -c 12 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 16)}"

install -m 0400 -o user1 /dev/null /home/user1/flag.txt
printf '%s\n' "$FLAG1" > /home/user1/flag.txt

install -m 0400 -o user2 /dev/null /home/user2/flag.txt
printf '%s\n' "$FLAG2" > /home/user2/flag.txt

# --- Generate SSH host keys ---
ssh-keygen -A

# --- Confirm layout ---
echo "=== Lab accounts ready ==="
grep -E '^(labadmin|user1|user2):' /etc/shadow | \
    awk -F: '{printf "  %-20s hash=%s\n", $1, $2}'
echo "  flag1 -> /home/user1/flag.txt"
echo "  flag2 -> /home/user2/flag.txt"
echo "==========================="
