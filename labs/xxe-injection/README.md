# XXE Injection: External Entity Expansion to File Read

A document processing service parses user-supplied XML with external entity expansion enabled. Injecting a DOCTYPE that maps an entity to `file:///flag.txt` causes the server to read the file and include it in the parsed output.

> This container binds to `127.0.0.1` only. Never expose port 8084 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/xxe-injection
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/xxe-injection
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/xxe-injection"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts are instant.

The lab listens on `127.0.0.1:8084`.

## Endpoint

| Method | Path | Content-Type | Description |
|--------|------|--------------|-------------|
| POST | `/upload` | `application/xml` | Parse an XML document and return item text |

## Docs

```
docs/01-introduction.md    what XXE is and why it matters
docs/02-background.md      XML entities, DOCTYPE, SYSTEM identifiers
docs/03-finding-the-bug.md confirming the parser expands external entities
docs/04-exploitation.md    crafting the XXE payload
docs/05-defense.md         disabling external entities and using safe parsers
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose
- curl or Python 3

## Installing Docker

**Kali / Debian / Ubuntu:**

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

Log out and back in after the last command.

**macOS:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

**Windows:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 backend, then run all commands inside a WSL2 terminal.
