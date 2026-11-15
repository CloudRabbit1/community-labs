#!/bin/sh
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag1.txt
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag2.txt
exec python3 /app/app.py
