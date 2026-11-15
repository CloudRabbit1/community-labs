# Path Traversal: Reading Files Outside the Document Root

A document server exposes a `/file` endpoint that reads files by name. The name is joined onto the document root without normalization, so a path like `../../flag.txt` walks above the root and reads arbitrary files on the filesystem.

> This container binds to `127.0.0.1` only. Never expose port 8082 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/path-traversal
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/path-traversal
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/path-traversal"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts are instant.

The lab listens on `127.0.0.1:8082`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List files in the document root |
| GET | `/file?name=<name>` | Read a file by name |

## Docs

```
docs/01-introduction.md    what path traversal is and why it matters
docs/02-background.md      how path joins work and where they go wrong
docs/03-finding-the-bug.md confirming the vulnerable parameter
docs/04-exploitation.md    crafting the traversal payload
docs/05-defense.md         canonicalization and allowlist fixes
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
