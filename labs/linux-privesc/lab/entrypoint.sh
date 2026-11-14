#!/bin/bash
set -e

FLAG1="POC{$(openssl rand -hex 16)}"
FLAG2="POC{$(openssl rand -hex 16)}"
FLAG3="POC{$(openssl rand -hex 16)}"
FLAG4="POC{$(openssl rand -hex 16)}"

install -m 0400 -o root -g root /dev/null /root/flag1.txt
install -m 0400 -o root -g root /dev/null /root/flag2.txt
install -m 0400 -o root -g root /dev/null /root/flag3.txt
install -m 0400 -o root -g root /dev/null /root/flag4.txt

printf '%s\n' "$FLAG1" > /root/flag1.txt
printf '%s\n' "$FLAG2" > /root/flag2.txt
printf '%s\n' "$FLAG3" > /root/flag3.txt
printf '%s\n' "$FLAG4" > /root/flag4.txt

# Generate SSH host keys if missing
ssh-keygen -A 2>/dev/null || true

exec /usr/sbin/sshd -D -e
