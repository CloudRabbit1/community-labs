#!/bin/sh
set -e

# Generate flag
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag.txt
chmod 644 /flag.txt

# Create document root with decoy files
mkdir -p /app/docs
printf 'Welcome to the document server.\n' > /app/docs/readme.txt
printf 'Company Policy v2.3\nAll employees must comply.\n' > /app/docs/policy.txt
printf 'Q3 sales: $1.2M\nQ4 target: $1.5M\n' > /app/docs/report.txt
