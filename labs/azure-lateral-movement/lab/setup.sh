#!/bin/sh
set -e
openssl rand -hex 32 > /storage_key.txt
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag.txt
chmod 644 /storage_key.txt /flag.txt
echo "[*] Lab ready"
