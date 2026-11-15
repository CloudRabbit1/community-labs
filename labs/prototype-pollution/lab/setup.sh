#!/bin/sh
set -e
# Generate a random flag at container start
FLAG="POC{$(node -e "process.stdout.write(require('crypto').randomBytes(16).toString('hex'))")}"
echo "$FLAG" > /flag.txt
chmod 644 /flag.txt
