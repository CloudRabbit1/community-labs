#!/bin/sh
set -e
# Write the flag to the vault volume at container startup.
# /vault is the named volume mounted by docker-compose.
mkdir -p /vault
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /vault/flag.txt
chmod 644 /vault/flag.txt
