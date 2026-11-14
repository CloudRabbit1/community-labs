#!/bin/sh
set -e
FLAG="POC{$(openssl rand -hex 16)}"
printf '%s\n' "$FLAG" > /flag.txt
chmod 644 /flag.txt
echo "[*] Lab ready — flag written to /flag.txt"
