# Finding the Bug

Start the lab:

```bash
docker compose up --build -d
```

Check the available endpoints:

```bash
curl http://localhost:8080/
```

Output:
```json
{
  "app": "NoteShare API v2.1",
  "note": "Prototype Pollution: __proto__ in merge target poisons Object.prototype",
  "endpoints": [
    "GET  /notes          list all notes",
    "POST /notes          save a note (body: {\"title\":\"...\",\"body\":\"...\"})",
    "POST /notes/merge    merge options into a note (body: {\"id\":\"...\",\"options\":{...}})",
    "GET  /admin/flag     read the flag (admin only)"
  ]
}
```

Confirm the admin endpoint is locked before any exploit:

```bash
curl http://localhost:8080/admin/flag
```

Output:
```json
{
  "error": "Admin only"
}
```

Create a note to get a valid ID:

```bash
curl -X POST http://localhost:8080/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"test","body":"hello"}'
```

Output:
```json
{
  "id": "lc2abc1def",
  "message": "Note saved"
}
```

Send a merge payload with a plain options key to confirm the endpoint works:

```bash
curl -X POST http://localhost:8080/notes/merge \
  -H "Content-Type: application/json" \
  -d '{"id":"lc2abc1def","options":{"color":"blue"}}'
```

Output:
```json
{
  "message": "Options merged",
  "options": {"color": "blue"}
}
```

The endpoint accepts arbitrary keys. The merge function recurses into nested objects. If a key is `__proto__`, the recursion targets `Object.prototype`.
