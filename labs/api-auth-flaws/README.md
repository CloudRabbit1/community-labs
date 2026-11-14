# api-auth-flaws: BOLA, BFLA, and mass assignment in a REST API

Exploit three authorization flaws in a JSON REST API: access another user's data by changing an ID, call an admin endpoint without admin privileges, and promote yourself to admin by over-posting a field the server should ignore.

> This container binds to `127.0.0.1` only. Never expose port 5000 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/api-auth-flaws
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/api-auth-flaws
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/api-auth-flaws"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 2 minutes. Subsequent starts use the cached image and are faster.

The API listens on `127.0.0.1:5000`.

## Accounts

| Account | Password | Purpose |
|---------|----------|---------|
| `alice` | `alice123` | your account (id=1) |
| `bob` | `bob123` | another user (id=2, holds flag1) |

## Flags

Three flags, one per vulnerability:

| Flag | Vulnerability | Endpoint |
|------|---------------|----------|
| flag1 | BOLA | `GET /api/users/2` |
| flag2 | BFLA | `GET /api/admin/users` |
| flag3 | Mass assignment | `PATCH /api/users/1` then `GET /api/admin/secret` |

## Docs

```
docs/01-introduction.md    what these bugs are and why they matter
docs/02-background.md      concepts you need before starting
docs/03-finding-the-bug.md mapping the API and spotting the flaws
docs/04-exploitation.md    capturing all three flags
docs/05-defense.md         how to fix each flaw
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose
- Linux, macOS, or Windows with WSL2
- x86_64 or AArch64 (Apple Silicon, ARM64)

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

Verify Docker is working:

```bash
docker run --rm hello-world
```
