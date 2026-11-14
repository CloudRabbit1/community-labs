#!/bin/bash
printf 'Content-Type: text/plain\r\n\r\n'

# Extract and URL-decode the host parameter from QUERY_STRING
HOST=$(python3 - << 'PYEOF'
import os, urllib.parse
qs = os.environ.get('QUERY_STRING', '')
params = urllib.parse.parse_qs(qs)
h = params.get('host', ['127.0.0.1'])[0]
print(h)
PYEOF
)

echo "Checking host: $HOST"
bash -c "ping -c 1 -W 1 $HOST" 2>&1
