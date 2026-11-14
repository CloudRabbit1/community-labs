#!/bin/bash
set -e

FLAG1="POC{$(openssl rand -hex 16)}"
FLAG2="POC{$(openssl rand -hex 16)}"

printf '%s\n' "$FLAG1" > /flag1.txt
printf '%s\n' "$FLAG2" > /flag2.txt
chmod 644 /flag1.txt /flag2.txt

exec python3 /app/app.py
