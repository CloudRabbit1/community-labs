#!/bin/sh
set -e
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag.txt
chmod 644 /flag.txt
