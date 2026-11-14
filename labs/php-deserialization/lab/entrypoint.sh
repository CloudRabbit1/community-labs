#!/bin/sh
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag1.txt
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag2.txt
mkdir -p /tmp/sessions
exec php -S 0.0.0.0:8080 -t /app /app/index.php
