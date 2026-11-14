#!/bin/bash
set -e

FLAG1="POC{$(openssl rand -hex 16)}"
FLAG2="POC{$(openssl rand -hex 16)}"

# flag1: in backup directory (exposed via directory listing)
mkdir -p /var/www/html/backup
cat > /var/www/html/backup/config.bak << CONFEOF
# Server configuration backup — do not expose publicly
db_host=10.10.0.5
db_user=webapp
db_pass=changeme123
api_key=
flag=$FLAG1
CONFEOF
chmod 644 /var/www/html/backup/config.bak

# flag2: accessible by www-data only (not publicly served)
mkdir -p /var/www/secret
printf '%s\n' "$FLAG2" > /var/www/secret/flag2.txt
chown www-data:www-data /var/www/secret/flag2.txt
chmod 600 /var/www/secret/flag2.txt

exec apache2ctl -D FOREGROUND
