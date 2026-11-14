#!/bin/bash
set -e

FLAG1="POC{$(openssl rand -hex 16)}"
FLAG2="POC{$(openssl rand -hex 16)}"

# flag1: readable via command injection on /api/ping
printf '%s\n' "$FLAG1" > /flag1.txt
chmod 644 /flag1.txt

# flag2: served by internal HTTP service on 127.0.0.1:9090
# only reachable by pivoting through the command injection
mkdir -p /internal
printf '%s\n' "$FLAG2" > /internal/index.html
chmod 644 /internal/index.html

# internal metrics service — not exposed externally
python3 -m http.server 9090 --bind 127.0.0.1 --directory /internal &

exec python3 /app/app.py
