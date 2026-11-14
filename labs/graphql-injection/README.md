# graphql-injection

GraphQL authentication bypass via broken login mutation. Introspection reveals a `login` mutation that accepts any password, returning a token and the first flag. The admin token unlocks an `adminPanel` query that holds the second flag.

CVE anchor: CVE-2024-32030 (Metabase GraphQL endpoint abuse).

## Prerequisites

- Docker and Docker Compose

## Quick start

```bash
docker compose up --build -d
# wait ~3s for the app to start
python3 exploit/exploit.py
```

The app binds to `127.0.0.1:8086`. Two flags are printed to stdout.

## Lab structure

```
graphql-injection/
├── README.md
├── docker-compose.yml
├── lab/
│   ├── Dockerfile
│   ├── app.py
│   └── entrypoint.sh
├── exploit/
│   └── exploit.py
├── docs/
│   ├── 01-introduction.md
│   ├── 02-background.md
│   ├── 03-finding-the-bug.md
│   ├── 04-exploitation.md
│   └── 05-defense.md
├── solutions/
│   └── walkthrough.md
└── test.sh
```

## Test

```bash
bash test.sh
```

Expected: 6 passed, 0 failed.
