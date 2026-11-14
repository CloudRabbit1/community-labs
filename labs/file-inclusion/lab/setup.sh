#!/bin/sh
set -e
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag.txt
chmod 644 /flag.txt
mkdir -p /app/pages
printf 'Welcome to the site. This page describes who we are.\n' > /app/pages/about.txt
printf 'Reach us at contact@example.com\n' > /app/pages/contact.txt
