# IDOR: Insecure Direct Object Reference

Exploit missing ownership checks in a document API to read another user's private file by enumerating integer IDs.

> This container binds to `127.0.0.1` only. Never expose port 8080 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/idor
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/idor
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/idor"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 30 to 60 seconds. Subsequent starts use the cached image and are instant.

The lab listens on `http://127.0.0.1:8080`.

## Accounts

| Account | Password    | Purpose                                     |
|---------|-------------|---------------------------------------------|
| `alice` | `password123` | Low-privilege user; document 1 is hers    |
| `admin` | `admin456`  | Admin account; document 2 contains the flag |

## Docs

```
docs/01-introduction.md    what this bug is and why it matters
docs/02-background.md      authentication vs authorisation explained
docs/03-finding-the-bug.md confirming the missing ownership check
docs/04-exploitation.md    scripted enumeration to retrieve the flag
docs/05-defense.md         ownership check fix and detection guidance
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose installed (see below if not installed)
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
