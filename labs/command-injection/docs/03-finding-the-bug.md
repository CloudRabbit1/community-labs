# Finding the Bug

Start the lab and confirm the service is running:

```bash
docker compose up --build -d
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

Send a normal ping request:

```bash
curl "http://localhost:8080/ping?host=127.0.0.1"
```

Output:
```json
{
  "command": "ping -c 3 127.0.0.1",
  "output": "PING 127.0.0.1 ...\n3 packets transmitted, 3 received, 0% packet loss",
  "injected": false
}
```

The `command` field shows exactly what the server runs. The user input goes directly into the command string with no quoting or escaping. Any shell metacharacter in the `host` parameter will be interpreted by the shell.
